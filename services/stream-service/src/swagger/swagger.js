const swaggerJsdoc = require('swagger-jsdoc')

const options = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'stream-service API',
            version: '1.0.0',
            description: 'stream-service swagger documentation'
        },
        servers: [{ url: 'http://localhost/api/stream/' }]
    },
    apis: ['src/routers/*.js'],
}
const swaggerSpec = swaggerJsdoc(options)

module.exports = swaggerSpec
