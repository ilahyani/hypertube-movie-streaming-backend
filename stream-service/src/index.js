const express = require('express')

app = express()

app.get('/api/stream', (req, res) => {
    return res.json({'message': 'stream service is up!'})
})

app.use('/api/stream/search', require('./routers/search'))

app.listen(process.env.PORT, () => {
    console.log(`stream service running on port ${process.env.PORT}`)
})