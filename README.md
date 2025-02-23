# 42-hypertube-movie-streaming-backend
Hypertube, Over Engineered Movie Streaming Platform Backend With Microservices Architecture

## Overview:
#### Project Description
This is the backend of a movie streaming web application where user can create accounts, search and stream movies and leave 
comments on movies.

#### The Stack
* FastAPI
* NodeJS
* PostgreSQL
* Psycopg
* Redis
* Nginx
* gRPC
* Docker

## Inter-service Communication: gRPC
gRPC (Google Remote Procedure Call) is used as the primary method of communication between microservices. gRPC is a high-performance, open-source framework that enables services to communicate with each other efficiently, using HTTP/2 as the transport protocol and Protocol Buffers (protobuf) as the serialization format for data exchange. It allows for the definition of services and their methods using a .proto file, which provide a clear structure for both the request and response formats. Each service exposes specific RPC (Remote Procedure Call) methods like loginService, signupService, getUserService, etc., for other services to invoke. For example, the AuthService manages user authentication requests, while the MovieService manages movie data. These services communicate with each other by sending requests and receiving responses in the form of structured data defined in the hyper.proto.

## Nginx
Nginx configuration sets up a reverse proxy for the microservices, handling different endpoints related to authentication, user management, and streaming. It listens on port 80 and routes requests to specific services based on the URL path. The /api/authorization path is used internally for authorization checks, proxying requests to an authorization-service without forwarding the body, while passing the original URI as a header. The /api/auth and /api/user paths forward requests to auth-service and user-service respectively, with necessary headers such as X-Real-IP and X-Forwarded-For for client information. The /api/user path also uses the auth_request directive to ensure the user is authenticated before passing the request to the user service, appending the X-User-ID header. For the /api/stream path, which handles streaming, it uses similar headers while enabling special configurations like disabling proxy buffering and setting timeouts to allow for continuous media streaming. The configuration also includes paths for API documentation (/api/auth/docs and /api/user/docs), which are proxied to the respective services, and an /openapi.json endpoint that dynamically selects the correct service based on the referer header. Any requests to other paths will return a 404 error, ensuring that only defined routes are processed.

## Video Streaming
This Node.js video streaming service combines torrent downloading with real-time streaming capabilities.

When a request for a movie is received, the server first checks if the movie is already downloaded. If it is, the server looks for a range request in the headers, which allows the client to stream a specific portion of the movie instead of the entire file. This is especially useful for large video files, as it allows the client to start streaming right away. The range is validated, and if it's valid, the server streams the requested chunk of the movie from the local file. This ensures smooth playback without requiring the user to wait for the whole file to be available.

If the movie isn’t fully downloaded but is partially available, the server streams the portion that has already been downloaded, while waiting for the rest of the file to finish downloading in the background. This is where the server uses the torrentStream library. It starts downloading the movie as a torrent, and once enough data has been buffered (i.e., enough chunks are downloaded), it begins streaming the data to the client. This allows the user to start watching the movie almost immediately, while the rest of the file continues to download in the background.

For movies that are not yet downloaded at all, the server uses the torrent library to download the movie file. The torrent engine manages the download, looking for suitable video files (like .mp4 or .mkv). As chunks of the movie are downloaded, the server writes them to disk and streams them to the client. This happens simultaneously—while the movie is being downloaded, the server is already serving the data the client requested. This ensures that the user can start streaming immediately and doesn’t need to wait for the entire file to be downloaded first.
