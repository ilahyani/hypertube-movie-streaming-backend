const router = require("express").Router({ mergeParams: true })
const torrentStream = require('torrent-stream')
const fs = require('fs')
const { Readable }  = require('stream')
const { addMovieRPC, getMovieRPC, updateMovieRPC } = require('../grpc/grpc_client')

const BUFFER_SIZE = 1024 * 1024 * 5

const stream_data = (range, movie_path, file_length, res) => {
    try {
        const { start, end } = validate_range(range, file_length)
        if (start == null || end == null) {
            res.status(400).json({ error: "Invalid Range" })
        }

        const buffer = Buffer.alloc(BUFFER_SIZE)
        fs.open(movie_path, 'r', (error, fd) => {
            if (error) {
                console.error('Failed to open file', error)
                return res.status(416).json({ error: 'streaming failed' })
            }
            fs.read(fd, buffer, 0, BUFFER_SIZE, start, (err, bytesRead) => {
                if (err) {
                    console.error('Failed to read file', err)
                    return res.status(416).json({ error: 'streaming failed' })
                }
                if (bytesRead === BUFFER_SIZE) {
                    console.log(`streaming range: ${start} - ${end}`)
                    const stream = Readable.from(buffer)
                    stream.pipe(res.status(206).header({
                        'Content-Range': `bytes ${start}-${end}/${file_length}`,
                        'Accept-Ranges': 'bytes',
                        'Content-Length': BUFFER_SIZE,
                        'Content-Type': 'video/mp4',
                        'Cache-Control': 'no-cache',
                        'Connection': 'Keep-Alive',
                        'Keep-Alive': 'timeout=60'
                    }))
                    
                    stream.on('error', (error) => {
                        console.error('Stream error', error)
                        if (!res.headersSent) {
                            res.status(416).json({ error: 'streaming failed' })
                        }
                        stream.destroy()
                    })
            
                    stream.on('end', () => {
                        console.log(`stream ended and read ${bytesRead} out of ${BUFFER_SIZE}`)
                    })
                } else {
                    console.log(`range: ${start} - ${end} is not available yet`)
                    res.status(416).json({ error: 'Range not available' })
                }
            })
        })

    } catch (error) {
        console.error('Streaming error', error)
        if (!res.headersSent) {
            res.status(500).json({ error: 'Failed to initialize stream' })
        }
    }
}

function stream_torrent(magnet, movie, movie_id, user_id, range, res) {

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

    engine.on('ready', async () => {
        try {
            console.log('Torrent is ready')
    
            const file = engine.files.find((file) => file.name.endsWith('.mp4') || file.name.endsWith('.mkv'))
            
            if (!file) {
                engine.destroy()
                return res.status(404).json({error: 'No supported video file found'})
            }
    
            movie = !movie ? movie = await addMovieRPC(movie_id, user_id, `/downloads/${file.name}`, file.length) : movie
            
            console.log('mv', movie)
    
            const readStream = file.createReadStream()
            const writeStream = fs.createWriteStream(movie.download_path, { mode: 0o644 })
    
            readStream.pipe(writeStream)
    
            readStream.on('error', (error) => {
                console.error('Read stream error:', error)
            })
    
            writeStream.on('error', (error) => {
                console.error('Write stream error:', error)
            })
    
            writeStream.on('finish', async () => {
                console.log(`File download complete: ${file.name}`)
                await updateMovieRPC(movie.id, true, null)
            })

            if (engine.swarm.downloaded < BUFFER_SIZE * 5) {
                await wait_download(engine)
            }

            stream_data(range, movie.download_path, file.length, res)
        } catch (error) {
            console.error('Torrent error', error)
            engine.destroy()
            if (!res.headersSent) {
                res.status(500).json({ error: 'Failed to process torrent' })
            }
        }
    })
    
    engine.on('download', async (chunk) => {
        console.log(`R: ${user_id}:${movie_id}: Downloading chunk ${chunk}`)
    })
    
    engine.on('idle', () => {
        console.log(`Torrent download complete`)
    })

    engine.on('error', (error) => {
        console.error('torrent engine error', error)
    })
}

const validate_range = (range, file_size) => {
    const start = parseInt(range.split('=')[1].split('-')[0])
    const end = Math.min(start + BUFFER_SIZE, file_size - 1)
    if ( start > file_size  || isNaN(start) || isNaN(end)) {
        return { start: null, end: null }
    }
    return { start, end }
}

const wait_download = async (engine) => {
    return new Promise((resolve) => {
        const intrvl_id = setInterval(() => {
            console.log(`WAITING FOR INITIAL BUFFER TO DOWNLOAD ... ${engine.swarm.downloaded} downloaded ouf of ${BUFFER_SIZE * 5}`)
            if (engine.swarm.downloaded >= BUFFER_SIZE * 5) {
                clearInterval(intrvl_id);
                resolve();
            }
        }, 2000);
    });
}

const update_last_watched = async (movie) => {
    const last_watched = new Date(movie.last_watched.split(" ")[0] || "")
    const last_day = new Date()
    last_day.setHours(last_day.getHours() - 24)

    if (last_watched <= last_day) {
        console.log(`UPDATING LAST_WATCHED FOR MOVIE ${movie.id}`)
        const update = await updateMovieRPC(movie.id, null, true)
        console.log('udpated:', update)
    }
}

/**
 * @swagger
 * /video:
 *   get:
 *     summary: Stream a movie
 *     parameters:
 *       - in: header
 *         name: range
 *         required: true
 *         description: Byte range for streaming
 *         schema:
 *           type: string
 *       - in: query
 *         name: movie_id
 *         required: true
 *         description: ID of the movie
 *         schema:
 *           type: string
 *       - in: query
 *         name: magnet
 *         required: true
 *         description: Magnet link for the movie
 *         schema:
 *           type: string
 *     responses:
 *       206:
 *         description: Partial content
 *         content:
 *           video/mp4:
 *             schema:
 *               type: string
 *               format: binary
 *       416:
 *         description: Requested range is not available, try again shortly
 *       400:
 *         description: Missing or invalid parameters
 *       500:
 *         description: Internal Server Error
 */

router.get('/', async (req, res) => {
    const range = req.headers.range
    const user_id = req.headers['x-user-id']
    const { movie_id, magnet } = req.query

    if (!range || !user_id || !movie_id || !magnet) {
        const missing = []
        if (!range) missing.push('range')
        if (!user_id) missing.push('user_id')
        if (!movie_id) missing.push('movie_id')
        if (!magnet) missing.push('magnet')
        
        return res.status(400).json({ error: `Missing required params: ${missing.join(', ')}` })
    }
    
    console.log(`NEW ${movie_id} REQUEST WITH RANGE: ${range}`)

    try {
        const movie = await getMovieRPC(movie_id)
        if (movie) {
            console.log(`${movie_id} MOVIE THERE ALREADY`, movie)

            await update_last_watched(movie)

            if (movie.downloaded && fs.existsSync(movie.download_path)) {
                console.log(`${movie_id} MOVIE FULLY DOWNLOADED`)
                const { start, end } = validate_range(range, movie.file_size)
                if (start == null || end == null) {
                    return res.status(400).json({ error: "Invalid Range" })
                }        
                fs.createReadStream(movie.download_path, { start, end }).pipe(res.status(206).header({
                        'Content-Range': `bytes ${start}-${end}/${movie.file_size}`,
                        'Accept-Ranges': 'bytes',
                        'Content-Length': BUFFER_SIZE,
                        'Content-Type': 'video/mp4',
                        'Cache-Control': 'no-cache',
                        'Connection': 'Keep-Alive',
                        'Keep-Alive': 'timeout=60'
                    }))
            } else {
                fs.open(movie.download_path, (err, data) => {
                    if (err) {
                        if (err.code === 'ENOENT') {
                            console.log(`${movie_id} MOVIE NOT DOWNLOADED`)
                            stream_torrent(magnet, movie, movie_id, user_id, range, res)
                        }
                        else {
                            console.error('Error opening file:', err);
                            return res.status(500).json({error: 'SERVER FAILED'})
                        }
                    } else {
                        console.log(`${movie_id} MOVIE PARTLY DOWNLOADED`)
                        stream_data(range, movie.download_path, movie.file_size, res)
                    }
                })
            }
        }
        else {
            console.log(`${movie_id} NEW MOVIE`)
            stream_torrent(magnet, null, movie_id, user_id, range, res)
        }
    }
    catch (error) {
        console.error('request failed', error)
        return res.status(500).json({error: 'SERVER FAILED'})
    }
})

module.exports = router
