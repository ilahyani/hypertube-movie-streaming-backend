const express = require('express')

app = express()

app.get('/api/stream', (req, res) => {
    return res.json({'message': 'stream service is up!'})
})

app.listen(process.env.PORT, () => {
    console.log(`stream service running on port ${process.env.PORT}`)
})