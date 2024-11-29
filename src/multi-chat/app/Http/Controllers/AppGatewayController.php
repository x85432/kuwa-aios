<?php

namespace App\Http\Controllers;

use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Message\RequestInterface;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\URL;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\App;
use GuzzleHttp\Client;
use GuzzleHttp\Psr7\Uri;

class AppGatewayController extends Controller
{
    const CONNECT_TIMEOUT_SEC = 60;
    const REQUEST_TIMEOUT_SEC = 300;

    /**
     * Acts as a gateway to forward requests to different applications based on the provided app_name.
     *
     * This function receives a request, modifies its target URI and headers, forwards it to the target application,
     * and streams the response back to the client.  It handles timeouts, redirects, and content decoding.
     *
     * @param \Psr\Http\Message\ServerRequestInterface $request The incoming request.
     * @param string $app_name The name of the target application.
     * @param string|null $app_path_segment  An optional path segment to append to the target URI.  Currently unused.
     * @return \Symfony\Component\HttpFoundation\StreamedResponse A streamed response from the target application.
     */
    public function gateway(ServerRequestInterface $request, $app_name, $app_path_segment = null)
    {
        $request = $this->alterTargetUri($request, $app_name);
        $request = $this->addHeaders($request, $this->createGatewayReqHeaders($request));
        $request = $this->addHeaders($request, $this->createKuwaReqHeaders($app_name));

        $client = new Client();
        $response = $client->send($request, [
            'timeout' => self::REQUEST_TIMEOUT_SEC,
            'connect_timeout' => self::CONNECT_TIMEOUT_SEC,
            'allow_redirects' => false, /* Disable following redirects. */
            'decode_content' => false,  /* Disable decode content. */
            'expect' => false,          /* Disable the additional "Expect: 100-Continue" header. */
            'http_errors' => false,     /* Disable throwing exception of HTTP error. */
            'stream' => true,           /* Enable streaming response. */
        ]);

        $response_headers = $response->getHeaders();
        $response_headers['X-Accel-Buffering'] = 'no';
        return response()->stream(
            $this->getResponseReader($response),
            $response->getStatusCode(),
            $response_headers
        );
    }
    
    /**
     * Adds an array of headers to a given request.
     *
     * @param \Psr\Http\Message\ServerRequestInterface $request The request to modify.
     * @param array $headers An associative array of headers to add (key => value).
     * @return \Psr\Http\Message\ServerRequestInterface The modified request with added headers.
     */
    private function addHeaders(ServerRequestInterface $request, array $headers) : ServerRequestInterface {
        foreach ($headers as $key => $value) {
            $request = $request->withHeader($key, $value);
        }
        return $request;
    }
    
    /**
     * Creates an array of gateway-related request headers.
     *
     * These headers provide information about the original request's host and protocol.
     *
     * @param \Psr\Http\Message\ServerRequestInterface $request The incoming request.
     * @return array An associative array of gateway headers.
     */
    private function createGatewayReqHeaders(ServerRequestInterface $request) : array {
        $host = $request->getHeaderLine('Host');
        $scheme = $request->getUri()->getScheme();
        $gateway_headers = [
            'Host' => $host,
            'X-Forwarded-Host' => $host,
            'X-Forwarded-Proto' => $scheme,
            'Connection' => 'close',
        ];
        return $gateway_headers;
    }


    /**
     * Creates an array of Kuwa-specific request headers.
     *
     * These headers include user authentication and application information.
     *
     * @param string|null $app_name The name of the target application.
     * @return array An associative array of Kuwa headers.
     */
    private function createKuwaReqHeaders(string $app_name = NULL) : array{
        $locale = App::getLocale();
        $rfc5646_locale = str_replace('_', '-', $locale);
        $kuwa_headers = [
            'Accept-Language' => $rfc5646_locale,
            'X-Kuwa-App-Name' => $app_name,
            'X-Kuwa-User-Id' => Auth::user()->id,
            'X-Kuwa-Api-Token' => Auth::user()->tokens()->where('name', 'API_Token')->first()->token,
            'X-Kuwa-Api-Base-Url' => URL::to('/'),
        ];

        return $kuwa_headers;
    }

    /**
     * Alters the request URI to point to the correct target application based on app_name.
     *
     * Uses a temporary in-memory database (TODO: replace with a persistent database).
     *
     * @param \Psr\Http\Message\ServerRequestInterface $request The incoming request.
     * @param string $app_name The name of the target application.
     * @return \Psr\Http\Message\ServerRequestInterface The modified request with the altered URI.
     * @throws \Illuminate\Support\Facades\abort 404 if the app_name is not found.
     */
    private function alterTargetUri(ServerRequestInterface $request, string $app_name) : ServerRequestInterface {
        # This is a temporal KV database for POC.
        # [TODO] Read app_root from database
        $app_root_db = [
            "com.kuwa.debug" => "http://host.docker.internal:7860",
            "com.github.jhj0517.whisper-webui" => "http://host.docker.internal:7861",
            "com.github.automatic1111.stable-diffusion-webui" => "http://host.docker.internal:7862",
            "com.kuwa.cad-webui" => "http://host.docker.internal:7863",
            "com.github.cinnamon.kotaemon" => "http://host.docker.internal:7864",
        ];
        abort_if(!array_key_exists($app_name, $app_root_db), 404);
        $request_uri = $request->getUri();
        $target_uri = new Uri($app_root_db[$app_name]);
        $target_uri = $target_uri->withPath($request_uri->getPath());
        $target_uri = $target_uri->withQuery($request_uri->getQuery());
        $request = $request->withUri($target_uri, preserveHost: true);

        return $request;
    }

    /**
     * Creates a closure that reads and streams the response body from a Guzzle response.
     *
     * This function is designed to stream the response in chunks to avoid memory issues with large responses.
     *
     * @param \GuzzleHttp\Psr7\Response $response The Guzzle response object.
     * @param int $chunk_size The size of each chunk to read (in bytes).
     * @return callable A closure that streams the response body.
     */
    private function getResponseReader(&$response, $chunk_size=1024)
    {
        $body_stream = $response->getBody();
        $reader = function() use (&$body_stream, $chunk_size) {
            while (!$body_stream->eof()) {
                echo $body_stream->read($chunk_size);
                ob_flush();
                flush();
            }
        };
        return $reader;
    }
}