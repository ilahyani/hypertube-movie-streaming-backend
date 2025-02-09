const router = require("express").Router({ mergeParams: true })
const torrentStream = require('torrent-stream')
const fs = require('fs')
const EventEmitter = require('node:events')
const { addMovieRPC, getMovieRPC } = require('../grpc/grpc_client')

const BUFFER_SIZE = 1024 * 1024 * 5
const eventEmitter = new EventEmitter()
const req_tracker = new Map

const stream_data = (start, end, movie_path, file_length, res) => {
    fs.createReadStream(movie_path, {start, end}).pipe(res.status(206).header({
            'Content-Range': `bytes ${start}-${end}/${file_length}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': end - start + 1,
            'Content-Type': 'video/mp4',
            'Cache-Control': 'no-cache',
            'Connection': 'Keep-Alive',
            'Keep-Alive': 'timeout=60'
        })
    )
}

function checkRange (movie_path, file_length, start, end, first_chunk, last_chunk, saved_chunks, requested, res) {
    if (requested.processed && fs.existsSync(movie_path)) {
        requested.processed = false
        console.log('checking requested range')
        for (let i = first_chunk; i <= last_chunk; i++) {
            if (!saved_chunks.includes(i)) {
                console.log('range is not ready')
                requested.processed = true
                break
            }
            if (i == last_chunk) {
                console.log('range is ready')
                eventEmitter.removeListener('check_range', () => {
                    checkRange(movie_path, file_length, start, end, first_chunk, last_chunk, saved_chunks, requested, res)
                })
                stream_data(start, end, movie_path, file_length, res)
            }
        }
    }
}

router.get('/', async (req, res) => {
    const range = req.headers.range
    const user_id = req.headers['x-user-id']
    const { movie_id, hash } = req.query

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
    
    let requested = { processed: true }
    
    try {
        if (req_tracker.has(`${user_id}${movie_id}`)) {

            console.log(req_tracker.get(`${user_id}${movie_id}`))

            const { downloaded, movie_path, saved_chunks, chunk_size, file_length } = req_tracker.get(`${user_id}${movie_id}`) || {}

            const start = parseInt(range.split('=')[1].split('-')[0])
            const end = Math.min(start + BUFFER_SIZE, file_length - 1)

            if ( isNaN(start) || start > file_length ) {
                return res.status(416).json({error: "Invalid Range"})
            }

            if (downloaded) {
                console.log(`MOVIE DOWNLOADED ALREADY`)

                stream_data(start, end, movie_path, file_length, res)
            }
            else {
                console.log(`MOVIE NOT FULLY DOWNLOADED YET`)

                const first_chunk = Math.floor(start / chunk_size)
                const last_chunk = Math.floor(end / chunk_size)

                eventEmitter.on('check_range', () => {
                    checkRange(movie_path, file_length, start, end, first_chunk, last_chunk, saved_chunks, requested, res)
                })
            }
        }
        else {
            const movie = await getMovieRPC(movie_id)

            if (movie && movie.downloaded) {
                console.log(`MOVIE DOWNLOADED ALREADY`)

                fs.stat(movie.download_path, (err, stats) => {
                    if (err) {
                        // delete db record -> downlaod and stream again!
                        console.error('Error getting file stats:', err);
                        return res.status(500).json({ error: 'Server Failed to Read File' });
                    }
                    req_tracker.set(`${user_id}${movie_id}`, {
                        download: true,
                        movie_path: movie.download_path,
                        file_length: stats.size,
                        saved_chunks: []
                    })
                    start = parseInt(range.split('=')[1].split('-')[0])
                    end = Math.min(start + BUFFER_SIZE, stats.size - 1)
                    if ( isNaN(start) || start > stats.size ) {
                        return res.status(416).json({error: "Invalid Range"})
                    }
                    stream_data(start, end, movie.download_path, stats.size, res)
                })
            }
            else {
                console.log(`MOVIE NOT FULLY DOWNLOADED YET`)

                const magnet = `magnet:?xt=urn:btih:${hash}`
                const engine = torrentStream(magnet, {
                    tmp: '/downloads',
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

                engine.on('ready', () => {
                    console.log('Torrent is ready')
    
                    const file = engine.files.find((file) => file.name.endsWith('.mp4') || file.name.endsWith('.mkv'))
                    if (!file) {
                        return res.status(404).json({error: 'We Got NADA'})
                    }

                    req_tracker.set(`${user_id}${movie_id}`, {
                        downloaded: false,
                        movie_path: `/downloads/${file.name}`,
                        file_length: file.length,
                        chunk_size: engine.torrent.pieceLength,
                        saved_chunks: []
                    })

                    const start = parseInt(range.split('=')[1].split('-')[0])
                    const end = Math.min(start + BUFFER_SIZE, file.length - 1)
                    if ( isNaN(start) || start > file.length ) {
                        return res.status(416).json({error: "Invalid Range"})
                    }
        
                    const readStream = file.createReadStream()
                    const writeStream = fs.createWriteStream(req_tracker.get(`${user_id}${movie_id}`).movie_path)

                    readStream.pipe(writeStream)
        
                    readStream.on('error', (error) => {
                        console.error('Read stream error:', error)
                    })
        
                    writeStream.on('error', (error) => {
                        console.error('Write stream error:', error)
                    })
            
                    writeStream.on('finish', async () => {
                        console.log(`File download complete: ${file.name}`)

                        try {
                            await addMovieRPC(movie_id, user_id, req_tracker.get(`${user_id}${movie_id}`).movie_path)
                            req_tracker.get(`${user_id}${movie_id}`).downloaded = true
                        } catch (error) {
                            console.error(error)
                            console.error('FAILED TO ADD MOVIE RECORD TO DB')
                        }
                    })

                    const chunk_size = engine.torrent.pieceLength
                    const first_chunk = Math.floor(start / chunk_size)
                    const last_chunk = Math.floor(end / chunk_size)

                    console.log(`RANGE: ${range} | ${start} - ${end} - | ${first_chunk} - ${last_chunk} | filesize: ${file.length}`) 

                    eventEmitter.on('check_range', () => {
                        checkRange(req_tracker.get(`${user_id}${movie_id}`).movie_path, file.length, start, end, first_chunk, last_chunk, req_tracker.get(`${user_id}${movie_id}`).saved_chunks, requested, res)
                    })
                })
                
                engine.on('download', (chunk) => {
                    console.log(`Request: ${user_id}${movie_id}: Downloading chunk ${chunk} for Movie ${movie_id}`)
                    req_tracker.get(`${user_id}${movie_id}`).saved_chunks.push(chunk)
                    eventEmitter.emit('check_range')
                })
                
                engine.on('idle', () => {
                    console.log(`Torrent download complete`)
                })
                engine.on('error', (error) => {
                    console.error(error)
                })
            }
        }
    }
    catch (error) {
        console.error(error)
        return res.status(500).json({error: 'SERVER FAILED'})
    }
})

module.exports = router
