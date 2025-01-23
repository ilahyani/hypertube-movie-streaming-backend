const router = require("express").Router({mergeParams: true});

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
        data.movies = data.movies.map((movie) => {
            // query movies table, if record exists, watched = true else watched = false
            return {
                id: movie.id,
                title: movie.title_english,
                year: movie.year,
                rating: movie.rating,
                thumbnail: movie.large_cover_image,
                watched: false
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
    const url = `https://yts.mx/api/v2/movie_details.json?movie_id=${movie_id}`
    try {
        const response = await fetch(url)
        if (!response.ok) {
            return res.status(500).json({ error: 'Failed to fetch data'})
        }
        const { data } = await response.json()
        return res.status(200).json({
            title: data.movie.title_english,
            summary: data.movie.description_full,
            year: data.movie.year,
            rating: data.movie.rating,
            genre: data.movie.genres,
            thumbnail: data.movie.large_cover_image,
            torrents: data.movie.torrents, 
            // subtitles
        })
    } catch (error) {
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

module.exports = router
