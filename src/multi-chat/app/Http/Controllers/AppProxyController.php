<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class AppProxyController extends Controller
{
    public function proxy(Request $request, $app_name, $uri = null)
    {
        // Determine the method of the incoming request
        $method = $request->method();

        // Prepare headers, including a custom header
        $headers = $request->headers->all();
        $host = $request->getHttpHost();
        $headers['Host'] = $host;
        $headers['X-ForwardedHost'] = $host;
        $headers['X-Kuwa-App-Name'] = $app_name; // Add your custom header here

        $app_root = 'http://127.0.0.1:7862';
        $url = $app_root . '/app/' . $app_name . '/' . $uri;

        // Forward the request to the specified URL
        $response = Http::withHeaders($headers)
            ->send($method, $url, [
                'query' => $request->query(),
                'body' => $request->getContent(),
            ]);

        // Return the response back to the client
        return response($response->body(), $response->status())
            ->withHeaders((object) $response->headers());
    }
}