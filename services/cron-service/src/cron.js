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
                    await updateMovieRPC(movie.id, false, null)
                }
            }
        })
    } catch (error) {
        console.error('cron ain\'t cronning!')
        console.error(error)
    }
})
