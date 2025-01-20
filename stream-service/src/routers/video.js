const router = require("express").Router({mergeParams: true})
const torrentStream = require('torrent-stream')
const fs = require('fs')

router.get('/', async (req, res) => {
    const range = req.headers.range?.split('=')[1] | null // bytes=0-
    try {
        // MKV file =====> https://www.npmjs.com/package/handbrake-js 
        // const magnet = "magnet:?xt=urn:btih:79816060ea56d56f2a2148cd45705511079f9bca&dn=TPB.AFK.2013.720p.h264-SimonKlose&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Fopen.demonii.com%3A1337&tr=udp%3A%2F%2Ftracker.c"
        // MP4 file
        const magnet = `magnet:?xt=urn:btih:B0158A04C937946FDE080D39862000036B630BE1&dn=${encodeURI("Rocky")}`
        const engine = torrentStream(magnet)
        engine.on('ready', () => {
            console.log('Torrent is ready')
            const file = engine.files.find((file) => file.name.endsWith('.mp4') || file.name.endsWith('.mkv'));
            if (!file) {
                return res.status(404).json({error: 'We Got NADA'})
            }
            console.log('Filename:', file.name)
            let start, end
            if (range) {
                start = parseInt(range.split('-')[0])
                end = parseInt(range.split('-')[1])
                if ( !start || start == NaN ) start = 0
                if ( !end || end == NaN ) end = file.length - 1
                if ( start > file.length ) {
                    return res.status(416).json({error: "invalid range"})
                }
            }
            else {
                start = 0
                end = file.length - 1
            }
            console.log(`>>>>>>>>>>>> RANGE: ${range} | start: ${start} | end: ${end}`) 
            res.writeHead(206, {
                'Content-Range': `bytes ${start}-${end}/${file.length}`,
                'Accept-Ranges': 'bytes',
                'Content-Length': end - start + 1,
                'Content-Type': 'video/mp4',
            })
            const stream = file.createReadStream({start, end})
            stream.pipe(fs.createWriteStream("downloads/torrent"))
            stream.pipe(res)
            })
            
            engine.on('download', (chunk) => {
                console.log('Downloading chunk:', chunk)
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
