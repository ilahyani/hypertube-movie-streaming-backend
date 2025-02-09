const express = require('express')

app = express()

app.get('/api/stream', (req, res) => {
    return res.json({'message': `stream service is up! ${req.headers['x-user-id']}`})
})

app.use(express.json())

app.use('/api/stream/comments', require('./routers/comments'))
app.use('/api/stream/search', require('./routers/search'))
app.use('/api/stream/video', require('./routers/video'))

app.listen(process.env.PORT, () => {
    console.log(`stream service running on port ${process.env.PORT}`)
})
