const router = require("express").Router({mergeParams: true})
const torrentStream = require('torrent-stream')
const fs = require('fs')

const magnet = `magnet:?xt=urn:btih:F5D61BF3D57082BA2EE1305DA5DF8DCD10D34539`
const saved_chunks = []

router.get('/', async (req, res) => {
    const range = req.headers.range
    if (!range) {
        return res.status(416).json({error: "Missing Range"})
    }
    try {
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
        engine.on('ready', () => {
            console.log('Torrent is ready')

            const file = engine.files.find((file) => file.name.endsWith('.mp4') || file.name.endsWith('.mkv'))
            if (!file) {
                return res.status(404).json({error: 'We Got NADA'})
            }

            const file_path = `downloads/${file.name}`
            const buffer_size = 1024 * 1024 * 5
            const start = parseInt(range.split('=')[1].split('-')[0])
            const end = Math.min(start + buffer_size, file.length - 1)
            if ( isNaN(start) || start > file.length ) {
                return res.status(416).json({error: "Invalid Range"})
            }
            
            console.log(`>>>>>>>>>>>> RANGE: ${range} | start: ${start} | end: ${end} | filesize: ${file.length}`) 

            // const readStream = file.createReadStream({ start, end })
            // const writeStream = fs.createWriteStream(file_path, { start, end })
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

            const chunk_size = engine.torrent.pieceLength
            const first_chunk = Math.floor(start / chunk_size)
            const last_chunk = Math.floor(end / chunk_size)
            
            let range_ready
            const intervalId = setInterval(() => {
                range_ready = false
                for (let i = first_chunk; i <= last_chunk; i++) {
                    if (!saved_chunks.includes(i)) {
                        break
                    }
                    if (i == last_chunk) {
                        range_ready = true
                    }
                }

                if (range_ready && fs.existsSync(file_path)) {
                    fs.open(file_path, 'r', (error, fd) => {
                        if (error) {
                            console.error(error)
                            return res.status(500).json({error: 'FAILED LVL 1'})
                        }

                        const length = end - start + 1
                        let buffer = Buffer.alloc(length)
                        fs.read(fd, buffer, 0, length, start, (error, bytesRead, buffer) => {
                            if (error) {
                                console.error(error)
                                return res.status(500).json({error: 'FAILED LVL 2'})
                            } 
                            fs.close(fd, (error) => {
                                if (error) {
                                    console.error(error)
                                    return res.status(500).json({error: 'FAILED LVL 3'})
                                } 
                            })
                            if (bytesRead >= length) {
                                console.log('bytesRead', bytesRead)
                                res.status(206).header({
                                    'Content-Range': `bytes ${start}-${end}/${file.length}`,
                                    'Accept-Ranges': 'bytes',
                                    'Content-Length': end - start + 1,
                                    'Content-Type': 'video/mp4',
                                }).send(buffer)
                                buffer = Buffer.alloc(0)
                                clearInterval(intervalId)
                            }
                        })
                    })
                }
            }, 200)
        })
        
        engine.on('download', (chunk) => {
            console.log('Downloading chunk:', chunk)
            saved_chunks.push(chunk)
        })
        
        engine.on('idle', () => {
            console.log('Torrent download complete')
        })
        engine.on('error', (error) => {
            console.log('WTF')
            console.error(error)
        })
    }
    catch (error) {
        console.error(error)
        res.status(500).json({error: 'DOWNLOAD FAILED'})
    }
})

module.exports = router
