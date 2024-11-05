<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Log;

class AppGatewayController extends Controller
{
    public function gateway(Request $request, $app_name, $uri = null)
    {
        // Determine the method of the incoming request
        $method = $request->method();

        // Prepare headers, including a custom header
        $headers = $request->headers->all();
        $host = $request->getHttpHost();
        $headers['Host'] = $host;
        $headers['X-ForwardedHost'] = $host;
        $headers['X-Kuwa-App-Name'] = $app_name;
        $headers['X-Kuwa-Api-Token'] = Auth::user()->tokens()->where('name', 'API_Token')->first()->token;
        $headers['X-Kuwa-User-Id'] = Auth::user()->id; 

        # This is a temporal KV database for POC.
        # [TODO] Read app_root from database
        $app_root_db = [
            "com.kuwa.debug" => "http://host.docker.internal:7860",
            "com.github.jhj0517.whisper-webui" => "http://host.docker.internal:7861",
            "com.github.automatic1111.stable-diffusion-webui" => "http://host.docker.internal:7862",
            "com.kuwa.cad-webui" => "http://host.docker.internal:7863",
        ];
        abort_if(!array_key_exists($app_name, $app_root_db), 404);
        $app_root = $app_root_db[$app_name];
        $url = $app_root . '/app/' . $app_name . '/' . $uri;

        // Forward the request to the specified URL
        // $rawRequestBody = file_get_contents('php://input');
        $rawRequestBody = $request->getContent();
        $response = Http::withHeaders($headers)
            ->send($method, $url, [
                'query' => $request->query(),
                'body' => $rawRequestBody,
            ]);

        // Return the response back to the client
        return response($response->body(), $response->status())
            ->withHeaders((object) $response->headers());
    }
}