const router = require("express").Router({mergeParams: true});

router.get('/', async (req, res) => {
    const query = req.query.q
    if (!query || query === "") {
        return res.status(200).json({})
    }
    const url = `https://yts.mx/api/v2/list_movies.json?query_term=${query}`
    try {
        const response = await fetch(url)
        if (!response.ok) {
            return res.status(500).json({ error: 'Internal Server Error'})
        }
        const data = await response.json()
        return res.status(200).json({ data: data.data })
    }
    catch (error) {
        console.error(error)
        return res.status(500).json({ error: 'Internal Server Error'})
    }
})

module.exports = router