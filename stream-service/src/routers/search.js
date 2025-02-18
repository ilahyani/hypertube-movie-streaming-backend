const router = require("express").Router({ mergeParams: true })
const { getUserMoviesRPC } = require("../grpc/grpc_client")
const TorrentSearchApi = require('torrent-search-api')

router.get('/', async (req, res) => {

    const user_id = req.headers['x-user-id']
    let { query, page, pageSize, sort, cursor } = req.query

    if (isNaN(page) || isNaN(pageSize)) {
        if (isNaN(page)) page = 0
        if (isNaN(pageSize)) page = 10
    }
    if (!query) {
        query = ""
        sort = 'r'
    }
    if (!sort) {
        sort = 't'
    }
    if (cursor === "") {
        cursor = null
    }

    let movies = [], nextCursorMark = null
    try {
        if (!cursor) {
            let url = `${process.env.YTS_API}/list_movies.json?query_term=${query}&limit=${pageSize}&page=${page}`
            if (sort == 'y') {
                url += `&order_by=asc&sort_by=year`
            }
            else if (sort == 'r') {
                url += `&order_by=asc&sort_by=rating`
            }
            else {
                url += `&order_by=asc&sort_by=title`
            }
            const response = await fetch(url)
            if (!response.ok) {
                return res.status(500).json({ error: 'Failed to fetch data'})
            }
            const { data } = await response.json()
            movies = data.movies
        }
        if (query && movies?.length == 0) {
            let url = `${process.env.IMDB_API}/search?originalTitle=${query}&type=movie&rows=${pageSize}`
            if (sort == 'r') {
                url += '&sortOrder=ASC&sortField=averageRating'
            }
            else if (sort == 'y') {
                url += '&sortOrder=ASC&sortField=startYear'
            }
            if (cursor) {
                url += `&cursorMark=${cursor}`
            }
            const response = await fetch(url, {
                    headers: {
                        'x-rapidapi-key': process.env.IMDB_API_Key
                    }
                }
            )
            if (!response.ok) {
                return res.status(500).json({ error: 'Failed to fetch data'})
            }
            const data = await response.json()
            movies = ( sort == 't' )
                ? data.results?.sort((a, b) => a.originalTitle.localeCompare(b.originalTitle))
                : data.results
            nextCursorMark = data.nextCursorMark
        }
        const movie_ids = movies.map((movie) => movie.imdb_code || movie.id)
        if (movie_ids.length > 0) {
            const watched_movies = await getUserMoviesRPC(movie_ids, user_id)
            movies = movies.map((movie) => {
                return {
                    id: movie.imdb_code || movie.id,
                    title: movie.title_english || movie.originalTitle, 
                    year: movie.year || movie.startYear,
                    rating: movie.rating || movie.averageRating,
                    thumbnail: movie.large_cover_image || movie.primaryImage,
                    watched: watched_movies?.includes((movie.imdb_code || movie.id).toString()) || false
                }
            })
        }
        if (nextCursorMark) {
            return res.status(200).json({ movies, nextCursorMark })
        }
        return res.status(200).json({ movies })
    }
    catch (error) {
        console.error(error)
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

router.get('/:id', async (req, res) => {

    const user_id = req.headers['x-user-id']
    const movie_id = req.params.id

    if (!movie_id) {
        res.status(400).json({ error: 'Missing movie id' })
    }

    try {
        const movie_data_response = await fetch(`${process.env.OMDB_API}&i=${movie_id}`)
        if (!movie_data_response.ok) {
            return res.status(500).json({ error: 'Failed to fetch data'})
        }
        const data = await movie_data_response.json()
        const watched_movies = await getUserMoviesRPC([movie_id], user_id)
        
        let torrents = []
        TorrentSearchApi.enableProvider('Yts')
        TorrentSearchApi.enableProvider('1337x')
        for (let resolution of ['720', '1080']) {
            torrent = await TorrentSearchApi.search(['Yts', '1337x'], `${data.Title} ${data.Year} ${resolution}`, 'Movies', 1)
            if (torrent.length > 0) {
                torrents.push({
                    resolution: resolution,
                    magnet: await TorrentSearchApi.getMagnet(torrent[0])
                })
            }
        }
        
        const subtitles_response = await fetch(`${process.env.OPENSUB_API}?imdb_id=${movie_id}&languages=en,fr`, {
            headers: {
                'Api-Key': process.env.OPENSUB_API_KEY
            }
        })
        let subtitles = await subtitles_response.json()
        if (subtitles.total_count > 0) {
            const en_sub = subtitles.data.filter(sub => sub.attributes.language === 'en')[0];
            const fr_sub = subtitles.data.filter(sub => sub.attributes.language === 'fr')[0];
            subtitles = [en_sub, fr_sub].map((sub) => {
                const { subtitle_id, language, url } = sub.attributes
                return  { subtitle_id, language, url }
            })
        }

        return res.status(200).json({
            title: data.Title,
            summary: data.Plot,
            year: data.Year,
            rating: data.imdbRating,
            genre: data.Genre,
            thumbnail: data.Poster,
            director: data.Director,
            writer: data.Writer,
            actors: data.Actors,
            country: data.Country,
            torrents: torrents,
            subtitles: subtitles,
            watched: watched_movies?.includes(data.imdbID.toString()) || false
        })
    } catch (error) {
        console.log(error)
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

module.exports = router
