const cron = require('node-cron')
const fs = require('fs');
const { updateMovieRPC, getMoviesRPC } = require('./grpc/grpc_client')

cron.schedule('0 0 * * * *', async () => {
        console.log('cron is cronning')
    try {
        const { movies } = await getMoviesRPC()
        movies?.forEach(async (movie) => {
            if (fs.existsSync(movie.download_path)) {
                const last_watched = new Date(movie.last_watched.split(" ")[0] || "")
                const last_month = new Date()
                last_month.setMonth(last_month.getMonth() - 1)
                if (last_watched <= last_month) {
                    console.log(`DELETING MOVIE ${movie.id} FROM SERVER`)
                    fs.unlinkSync(movie.download_path);
                    await updateMovieRPC(movie.id)
                }
            }
        })
        const files = fs.readdirSync('/downloads')
        const downloaded_movies = files?.filter(((file) => file.includes('.mp4') || file.includes('.mkv')))
        const db_movies = movies?.map((movie) => movie?.download_path?.split('/downloads/')[1])
        const orphan_files = downloaded_movies.filter((movie) => !db_movies.includes(movie))
        console.log('orphan_files', orphan_files)
        if (orphan_files.length > 0) {
           for (const file of orphan_files) {
                console.log(`DELETING ORPHAN FILE ${file} FROM SERVER`);
                fs.unlinkSync(`/downloads/${file}`);
            }
        }
    } catch (error) {
        console.error('cron ain\'t cronning!')
        console.error(error)
    }
})
