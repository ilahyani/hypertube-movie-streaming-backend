const router = require('express').Router({ mergeParams: true })
const { addCommentRPC, getCommentsRPC } = require('../grpc/grpc_client')

/**
 * @swagger
 * /comments:
 *   get:
 *     summary: Get comments for a movie
 *     parameters:
 *       - in: query
 *         name: movie_id
 *         required: true
 *         description: ID of the movie
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: A list of comments
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 comments:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       id:
 *                         type: string
 *                       author_id:
 *                         type: string
 *                       movie_id:
 *                         type: string
 *                       date:
 *                         type: string
 *                       comment:
 *                         type: string
 *       400:
 *         description: Missing movie id
 *       500:
 *         description: Failed to get movie comments
 */

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

/**
 * @swagger
 * /comments/new:
 *   post:
 *     summary: Add a new comment to a movie
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               movie_id:
 *                 type: string
 *               comment:
 *                 type: string
 *     responses:
 *       200:
 *         description: Successfully added comment
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *       500:
 *         description: Failed to add comment
 */

router.post('/new', async (req, res) => {
    const { movie_id, comment } = req.body
    const user_id = req.headers['x-user-id']
    try {
        const result = await addCommentRPC(movie_id, user_id, comment)
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
