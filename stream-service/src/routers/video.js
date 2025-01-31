const router = require("express").Router({ mergeParams: true })
const torrentStream = require('torrent-stream')
const fs = require('fs')
const EventEmitter = require('node:events')
const { addMovieRPC, getMovieRPC } = require('../grpc/grpc_client')

// const saved_chunks = new Set()
const saved_chunks = {}
const eventEmitter = new EventEmitter()

// keep track of clients request and prevent repeated proccessing of data 
request_data = {
    'req_id?????????????????///': {
        processed: false,
        torrent: false, // wether the movie is torrenting or not, if yes check saved chunks before serving
        movie_path: null,
        saved_chunks: []
    }
}

router.get('/', async (req, res) => {
    const range = req.headers.range
    const { user_id, movie_id, hash } = req.query

    if (!range) {
        return res.status(416).json({error: "Missing Range"})
    }
    if (!user_id) {
        return res.status(400).json({error: "Missing User ID"})
    }
    if (!movie_id) {
        return res.status(400).json({error: "Missing Movie ID"})
    }
    if (!hash) {
        return res.status(400).json({error: "Missing Movie Hash"})
    }
    try {
        /////////// this will run everytime a range is requested
        let movie = await getMovieRPC(movie_id)
        if (!movie.downloaded) {} // torrent
        else {} // stream
        if (!saved_chunks[hash]) {
            saved_chunks[hash] = []
        }
        const magnet = `magnet:?xt=urn:btih:${hash}`
        const engine = torrentStream(magnet, {
            tmp: 'downloads',
            tracker: true,
            trackers: [
                'udp://open.demonii.com:1337/announce',
                'udp://tracker.openbittorrent.com:80',
                'udp://tracker.coppersurfer.tk:6969',
                'udp://glotorrents.pw:6969/announce',
                'udp://tracker.opentrackr.org:1337/announce',
                'udp://torrent.gresille.org:80/announce',
                'udp://p4p.arenabg.com:1337',
                'udp://tracker.leechers-paradise.org:6969',
                'udp://tracker.ccc.de:80'
            ]
        })

        let file_path, buffer_size, start, end, chunk_size, first_chunk, last_chunk, requested = true
        engine.on('ready', () => {
            console.log('Torrent is ready')

            const file = engine.files.find((file) => file.name.endsWith('.mp4') || file.name.endsWith('.mkv'))
            if (!file) {
                return res.status(404).json({error: 'We Got NADA'})
            }

            file_path = `downloads/${file.name}`
            buffer_size = 1024 * 1024 * 5
            start = parseInt(range.split('=')[1].split('-')[0])
            end = Math.min(start + buffer_size, file.length - 1)
            if ( isNaN(start) || start > file.length ) {
                return res.status(416).json({error: "Invalid Range"})
            }
            chunk_size = engine.torrent.pieceLength
            first_chunk = Math.floor(start / chunk_size)
            last_chunk = Math.floor(end / chunk_size)
            console.log(`RANGE: ${range} | ${start} - ${end} - | ${first_chunk} - ${last_chunk} | filesize: ${file.length}`) 

            const readStream = file.createReadStream()
            const writeStream = fs.createWriteStream(file_path)
            readStream.pipe(writeStream)

            readStream.on('error', (error) => {
                console.error('Read stream error:', error)
                res.status(500).json({ error: 'STREAM FAILED' })
            })

            writeStream.on('error', (error) => {
                console.error('Write stream error:', error)
                res.status(500).json({ error: 'DOWNLOAD FAILED' })
            })
    
            writeStream.on('finish', () => {
                console.log('File download complete')
            })

            const checkRange = () => {
                if (requested && fs.existsSync(file_path)) {
                    requested = false
                    console.log('checking requested range')
                    for (let i = first_chunk; i <= last_chunk; i++) {
                        if (!saved_chunks[hash].includes(i)) {
                            console.log('range is not ready')
                            requested = true
                            break
                        }
                        if (i == last_chunk) {
                            eventEmitter.removeListener('check_range', checkRange)
                            console.log('range is ready')
                            res.status(206).header({
                                'Content-Range': `bytes ${start}-${end}/${file.length}`,
                                'Accept-Ranges': 'bytes',
                                'Content-Length': end - start + 1,
                                'Content-Type': 'video/mp4',
                                'Cache-Control': 'no-cache',
                                'Connection': 'Keep-Alive',
                                'Keep-Alive': 'timeout=60'
                            });
                            fs.createReadStream(file_path, {start, end}).pipe(res)
                        }
                    }
                }
            }

            eventEmitter.on('check_range', checkRange)
        })
        
        engine.on('download', (chunk) => {
            console.log('Downloading chunk:', chunk)
            saved_chunks[hash].push(chunk)
            eventEmitter.emit('check_range')
        })
        
        engine.on('idle', () => {
            console.log('Torrent download complete')
        })
        engine.on('error', (error) => {
            console.error(error)
            res.status(500).json({ error: 'ENGINE FAILED' })
        })
    }
    catch (error) {
        console.error(error)
        res.status(500).json({error: 'SERVER FAILED'})
    }
})

module.exports = router
