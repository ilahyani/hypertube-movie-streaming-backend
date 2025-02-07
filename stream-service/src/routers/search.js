const router = require("express").Router({ mergeParams: true });
const { getUserMoviesRPC } = require("../grpc/grpc_client")

router.get('/', async (req, res) => {
    let { query, page, pageSize, sort } = req.query
    if (isNaN(page) || isNaN(pageSize)) {
        return res.status(400).json({error: 'Invalid page or pageSize parameters'})
    }
    if (!sort) {
        sort = 'title'
    } else if (!['title', 'year', 'rating'].includes(sort)) {
        return res.status(400).json({error: 'Invalid sort parameter'})
    }
    if (!query) {
        query = ""
        sort = "rating"
    }
    const url = `https://yts.mx/api/v2/list_movies.json?sort_by=${sort}&query_term=${query}&limit=${pageSize}&page=${page}`
    console.log(url)
    try {
        const response = await fetch(url)
        if (!response.ok) {
            return res.status(500).json({ error: 'Failed to fetch data'})
        }
        const { data } = await response.json()
        const movie_ids = data.movies.map((movie) => movie.id)
        const watched_movies = await getUserMoviesRPC(movie_ids, '')
        data.movies = data.movies.map((movie) => {
            return {
                id: movie.id,
                title: movie.title_english,
                year: movie.year,
                rating: movie.rating,
                thumbnail: movie.large_cover_image,
                watched: watched_movies?.includes(movie.id.toString()) || false
            }
        })
        return res.status(200).json({ data })
    }
    catch (error) {
        console.error(error)
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

router.get('/:id', async (req, res) => {
    const movie_id = req.params.id
    if (!movie_id) {
        res.status(400).json({ error: 'Missing movie id' })
    }
    // await addMovieRPC(movie_id, '', 'downlaods/moviex')
    const url = `https://yts.mx/api/v2/movie_details.json?movie_id=${movie_id}`
    try {
        const response = await fetch(url)
        if (!response.ok) {
            return res.status(500).json({ error: 'Failed to fetch data'})
        }
        const { data } = await response.json()
        const movie_ids = [movie_id]
        const watched_movies = await getUserMoviesRPC(movie_ids, '')
        return res.status(200).json({
            title: data.movie.title_english,
            summary: data.movie.description_full,
            year: data.movie.year,
            rating: data.movie.rating,
            genre: data.movie.genres,
            thumbnail: data.movie.large_cover_image,
            torrents: data.movie.torrents, 
            watched: watched_movies?.includes(data.movie.id.toString()) || false
            // subtitles
        })
    } catch (error) {
        console.log(error)
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

module.exports = router
