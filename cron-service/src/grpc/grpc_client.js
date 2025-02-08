const grpc = require('@grpc/grpc-js')
const protoLoader = require('@grpc/proto-loader')
const PROTO_PATH = '/grpc/user.proto'

const grpc_server = `${process.env.GRPC_SERVER_HOST}:${process.env.GRPC_SERVER_PORT}`
const packageDef = protoLoader.loadSync(PROTO_PATH, { keepCase: true })
const proto = grpc.loadPackageDefinition(packageDef).user

getMoviesRPC = () => {
    console.log('getMoviesRPC CALL')
    
    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.getMovies({}, (err, response) => {
            if (err) {
                console.log('getMoviesRPC ERROR:', err)
                reject(err)
            }
            console.log('getMoviesRPC RESPONSE:', response)
            resolve(response)
        })
    })
}

updateMovieRPC = (movie_id) => {
    console.log('updateMovieRPC CALL')

    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.updateMovie({ movie_id }, (err, response) => {
            if (err) {
                console.error('updateMovieRPC ERROR:', err)
                reject(err)
            }
            // console.log('updateMovieRPC RESPONSE:', response)
            resolve (response)
        })
    })
}

deleteMovieRPC = (movie_id) => {
    console.log('deleteMovieRPC CALL')
    
    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.deleteMovie({ movie_id }, (err, response) => {
            if (err) {
                console.error('deleteMovieRPC ERROR:', err)
                reject(err)
            }
            // console.log('deleteMovieRPC RESPONSE:', response)
            resolve (response)
        })
    })
}

module.exports = { updateMovieRPC, deleteMovieRPC, getMoviesRPC }
