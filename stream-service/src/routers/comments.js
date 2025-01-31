const router = require('express').Router({ mergeParams: true })
const { addCommentRPC, getCommentsRPC } = require('../grpc/grpc_client')

router.get('/', async (req, res) => {
    const { movie_id } = req.query
    if (!movie_id) {
        res.status(400).json({ error: 'Missing movie id' })
    }
    try {
        const comments = await getCommentsRPC(movie_id)
        return res.status(200).json({ comments })
    } catch (error) {
        console.error(error)
        return res.status(500).json({ error: 'Failed to get movie comments'})
    }
})

router.post('/new', async (req, res) => {
    const { movie_id, comment } = req.body
    try {
        const result = await addCommentRPC(movie_id, 'ca17e1a5-aec8-482d-a159-d86f8bd1b55c', comment)
        if (!result) {
            return res.status(500).json({ error: 'Failed to add comment'})
        }
        return res.status(200).json({ success: result })
    } catch (error) {
        console.error(error)
        return res.status(500).json({ error: 'Failed to add comment'})
    }
})

module.exports = router
