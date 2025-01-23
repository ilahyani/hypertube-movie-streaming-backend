const router = require('express').Router({ mergeParams: true })

router.get('/', (req, res) => {
    const { movie_id } = req.query
    if (!movie_id) {
        res.status(400).json({ error: 'Missing movie id' })
    }
    // query comments table through grpc client
})

router.post('/new', (req, res) => {
    const { movie_id, comment } = req.body.json()
    // insert new record to comments table through grpc client
})

module.exports = router
