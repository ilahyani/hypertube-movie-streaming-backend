const express = require('express')
const cors = require('cors')

app = express()

app.get('/api/stream', (req, res) => {
    return res.json({'message': `stream service is up! ${req.headers['x-user-id']}`})
})

app.use(express.json())

app.use(cors())

app.use('/api/stream/comments', require('./routers/comments'))
app.use('/api/stream/search', require('./routers/search'))
app.use('/api/stream/video', require('./routers/video'))

app.use('/api/stream/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec))

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

app.listen(process.env.PORT, () => {
    console.log(`stream service running on port ${process.env.PORT}`)
})
