const grpc = require('@grpc/grpc-js')
const protoLoader = require('@grpc/proto-loader')
const { response, query } = require('express')
const PROTO_PATH = '/grpc/user.proto'

const grpc_server = `${process.env.GRPC_SERVER_HOST}:${process.env.GRPC_SERVER_PORT}`
const packageDef = protoLoader.loadSync(PROTO_PATH, { keepCase: true })
const proto = grpc.loadPackageDefinition(packageDef).user

addMovieRPC = (movie_id, user_id, download_path) => {
    console.log('addMovieRPC CALL')
    
    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.addMovie({ movie_id, user_id, download_path}, (err, response) => {
            if (err) {
                console.log('addMovieRPC ERROR:', err)
                reject(err)
            }
            console.log('addMovieRPC RESPONSE:', response)
            resolve (response?.movie)
        })

    })
}

getMovieRPC = (movie_id) => {
    console.log('getMovieRPC CALL')
    
    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.getMovie({ movie_id }, (err, response) => {
            if (err) {
                console.log('getMovieRPC ERROR:', err)
                reject(err)
            }
            console.log('getMovieRPC RESPONSE:', response)
            resolve(response?.movie)
        })
    })
}

getUserMoviesRPC = (movie_ids, user_id) => {
    console.log('getUserMoviesRPC CALL')
    
    return new Promise((resolve, reject) => {
        const client = new proto.MovieService(grpc_server, grpc.credentials.createInsecure())
        client.getUserMovies({ movie_ids, user_id }, (err, response) => {
            if (err) {
                console.log('getUserMoviesRPC ERROR:', err)
                reject(err)
            }
            console.log('getUserMoviesRPC RESPONSE:', response, typeof response?.movie_ids)
            resolve(response?.movie_ids)
        })
    })
}

addCommentRPC = (movie_id, author_id, comment) => {
    console.log('addCommentRPC INIT')

    return new Promise((resolve, reject) => {
        const client = new proto.CommentService(grpc_server, grpc.credentials.createInsecure())
        client.addComment({ author_id, movie_id, comment }, (err, response) => {
            if (err) {
                console.log('addCommentRPC ERROR:', err)
                reject(err)
            }
            console.log('addCommentRPC RESPONSE:', response)
            resolve(response?.success)
        })
    })
}

getCommentsRPC = (movie_id) => {
    console.log('getCommentsRPC INIT')

    return new Promise((resolve, reject) => {
        const client = new proto.CommentService(grpc_server, grpc.credentials.createInsecure())
        client.getComments({ movie_id }, (err, response) => {
            if (err) {
                console.log('getCommentsRPC ERROR:', err)
                reject(err)
            }
            console.log('getCommentsRPC RESPONSE:', response)
            resolve(response?.comments)
        })
    })
}

module.exports = { addMovieRPC, getMovieRPC, getUserMoviesRPC, addCommentRPC, getCommentsRPC }
