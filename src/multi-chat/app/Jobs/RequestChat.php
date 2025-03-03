<?php

namespace App\Jobs;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use App\Models\User;
use Illuminate\Bus\Queueable;
use App\Events\RequestStatus;
use App\Models\Histories;
use GuzzleHttp\Client;
use Carbon\Carbon;

class RequestChat implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;
    private $input, $access_code, $msgtime, $history_id, $user_id, $channel, $lang, $openai_token, $google_token, $third_party_token, $user_token, $modelfile, $preserved_output, $exit_when_finish, $nim_token;
    public $tries = 100; # Wait 1000 seconds in total
    public $timeout = 1200; # For the 100th try, 200 seconds limit is given
    public static $kernel_api_version = 'v1.0';
    public $filters = ["[Sorry, There're no machine to process this LLM right now! Please report to Admin or retry later!]", '[Oops, the LLM returned empty message, please try again later or report to admins!]', '[有關Kuwa的相關說明，請以 kuwaai.org 官網的資訊為準。]', '[Sorry, something is broken, please try again later!]'];

    /**
     * Create a new job instance.
     */

    public function processModelfile($modelfile)
    {
        $excludedNames = ['prompts', 'start-prompts', 'auto-prompts', 'welcome'];

        return $modelfile
            ? json_encode(
                array_values(
                    array_filter(
                        array_map(function ($entry) use ($excludedNames) {
                            if (!in_array($entry->name, $excludedNames, true) && !empty($entry->name) && $entry->name[0] !== '#') {
                                $entry->args = str_starts_with($entry->args, '"') ? trim($entry->args, '"') : $entry->args;
                                return $entry;
                            }
                        }, $modelfile),
                    ),
                ),
            )
            : null;
    }

    public function __construct($input, $access_code, $user_id, $history_id, $lang, $channel = null, $modelfile = null, $preserved_output = '', $exit_when_finish = true)
    {
        $this->input = json_encode(json_decode($input), JSON_UNESCAPED_UNICODE);
        $this->msgtime = date('Y-m-d H:i:s', strtotime(date('Y-m-d H:i:s') . ' +1 second'));
        $this->access_code = $access_code;
        $this->user_id = $user_id;
        $this->lang = $lang;
        $this->history_id = $history_id;
        $this->exit_when_finish = $exit_when_finish;
        if ($channel == null) {
            $channel = '';
        }
        $this->preserved_output = $preserved_output;
        $this->channel = $channel;
        $this->modelfile = $this->processModelfile($modelfile);
        $user = User::find($user_id);
        $this->openai_token = $user->openai_token;
        $this->google_token = $user->google_token;
        $this->nim_token = $user->nim_token;
        $this->third_party_token = $user->third_party_token;
        if ($user->tokens()->where('name', 'API_Token')->count() != 1) {
            $user->tokens()->where('name', 'API_Token')->delete();
            $user->createToken('API_Token', ['access_api']);
        }
        $this->user_token = $user->tokens()->where('name', 'API_Token')->first()->token;
    }

    /**
     * Read an GuzzleHttp stream.
     *
     * [Deprecated] Since 0.4.0, we use SSE stream with JSON payload to handle internal response.
     * Reading raw byte stream is deprecated and should be removed in the future.
     */
    private function read_stream(&$stream, $timeout_sec = 0.1)
    {
        $buffer = '';
        $start_time = microtime(true);
        while (!$stream->eof() && microtime(true) - $start_time < $timeout_sec) {
            $chunk = $stream->read(1);
            $buffer .= $chunk;
        }
        return $buffer;
    }

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        $warningMessages = [];
        if ($this->channel == '') {
            $this->channel .= $this->history_id;
        }
        Log::channel('analyze')->Info($this->channel);
        if ($this->history_id > 0 && $this->channel == $this->history_id . '') {
            if (Histories::find($this->channel) && Histories::find($this->channel)->msg != '* ...thinking... *' && $this->preserved_output == '') {
                Log::Debug('Hmmm');
                return;
            }
        }
        Log::channel('analyze')->Info('In:' . $this->access_code . '|' . $this->user_id . '|' . $this->history_id . '|' . strlen(trim($this->input)) . '|' . trim($this->input) . '|' . $this->lang . '|' . $this->modelfile);
        $start = microtime(true);
        $tmp = '';
        try {
            $kernel_location = \App\Models\SystemSetting::where('key', 'kernel_location')->first()->value;
            $client = new Client(['timeout' => 300]);
            $response = $client->post($kernel_location . '/' . self::$kernel_api_version . '/worker/schedule', [
                'headers' => ['Content-Type' => 'application/x-www-form-urlencoded'],
                'form_params' => [
                    'name' => $this->access_code,
                    'history_id' => $this->history_id * ($this->channel == $this->history_id ? 1 : -1),
                    'user_id' => $this->user_id,
                ],
                'stream' => true,
            ]);
            $state = trim($response->getBody()->getContents());
            if ($state == 'BUSY') {
                $this->release(10);
            } elseif ($state == 'NOMACHINE') {
                $tmp = "[Sorry, There're no machine to process this LLM right now! Please report to Admin or retry later!]";
                try {
                    if ($this->channel == '' . $this->history_id) {
                        $history = Histories::find($this->history_id);
                        if ($history != null) {
                            $history->fill(['msg' => $tmp]);
                            $history->save();
                        }
                    }
                } catch (Exception $e) {
                }
                Log::channel('analyze')->Info('NOMACHINE: ' . $this->access_code . ' | ' . $this->history_id . '|' . strlen(trim($this->input)) . '|' . trim($this->input));

                Redis::publish($this->channel, 'New ' . json_encode(['msg' => trim($tmp)]));
                Redis::publish($this->channel, 'Ended Ended');
                $msgTimeInSeconds = Carbon::createFromFormat('Y-m-d H:i:s', $this->msgtime)->timestamp;
                $currentTimeInSeconds = Carbon::now()->timestamp;
                $ExecutionTime = $currentTimeInSeconds - $msgTimeInSeconds;

                if ($ExecutionTime < 5) {
                    sleep(5 - $ExecutionTime);
                }
                Redis::lrem(($this->channel == $this->history_id ? 'usertask_' : 'api_') . $this->user_id, 0, $this->history_id);

                Redis::publish($this->channel, 'New ' . json_encode(['msg' => trim($tmp)]));
                Redis::publish($this->channel, 'Ended Ended');
            } elseif ($state == 'READY') {
                try {
                    $test = json_decode($this->input);

                    if ($test === false && json_last_error() !== JSON_ERROR_NONE) {
                        //There're error in the json!
                        //which shouldn't be happening...
                        Log::channel('analyze')->Info("How does that happened? JSON decode error in the Job!\n" . $this->input);
                        return;
                    } else {
                        $test_2 = collect(json_decode($this->input))
                            ->where('isbot', false)
                            ->last();
                        if ($test_2 !== null) {
                            $kuwa_flag = strpos(strtoupper($test_2->msg), strtoupper('kuwa')) !== false;

                            foreach ($test as $t) {
                                foreach ($this->filters as $filter) {
                                    if (strpos($t->msg, $filter) !== false) {
                                        $t->msg = trim(str_replace($filter, '', $t->msg));
                                    }
                                }
                                if ($t->isbot) {
                                    $t->msg = preg_replace('#<<<WARNING>>>.*?<<</WARNING>>>#s', '', $t->msg);
                                }
                            }
                            $this->input = json_encode($test);
                        } else {
                            $kuwa_flag = false;
                        }
                        if (trim(\App\Models\SystemSetting::where('key', 'safety_guard_location')->first()->value) !== '') {
                            $kuwa_flag = false;
                        }
                    }
                    $response = $client->post($kernel_location . '/' . self::$kernel_api_version . '/chat/completions', [
                        'headers' => [
                            'Content-Type' => 'application/x-www-form-urlencoded',
                            'Accept-Language' => $this->lang,
                            'X-Kuwa-User-Id' => $this->user_id,
                            'X-Kuwa-Api-Token' => $this->user_token,
                            'X-Kuwa-Api-Base-Urls' => config('app.KUWA_API_BASE_URLS'),
                        ],
                        'form_params' => [
                            'input' => $this->input,
                            'name' => $this->access_code,
                            'user_id' => $this->user_id,
                            'history_id' => $this->history_id * ($this->channel == $this->history_id ? 1 : -1),
                            'openai_token' => $this->openai_token,
                            'google_token' => $this->google_token,
                            'nim_token' => $this->nim_token,
                            'third_party_token' => $this->third_party_token,
                            'user_token' => $this->user_token,
                            'modelfile' => $this->modelfile,
                        ],
                        'stream' => true,
                    ]);
                    $stream = $response->getBody();
                    $buffer = new Utf8Buffer();
                    $insideTag = false;
                    $cache = false;
                    $cached = '';
                    while (!$stream->eof()) {
                        // $chunk = $this->read_stream($stream);
                        $chunk = \GuzzleHttp\Psr7\Utils::readLine($stream);
                        // Extract text response from SSE data
                        if (str_starts_with($chunk, "data: ")){
                            $json = substr($chunk, strlen("data: "));
                            $resp = json_decode($json, true);
                            $resp_chunks = $resp['delta'] ?? array();
                            $chunk = "";
                            foreach($resp_chunks as $resp_chunk){
                                $type = $resp_chunk["type"] ?? null;
                                if ($type !== 'text') continue;
                                $chunk .= $resp_chunk["text"]["value"] ?? '';
                            }
                        }
                        $buffer .= $chunk;
                        $bufferLength = mb_strlen($buffer, '8bit');
                        $messageLength = null;
                        for ($i = $bufferLength; $i > 0 ; $i--) {
                            $message = mb_substr($buffer, 0, $i, '8bit');
                            if (mb_check_encoding($message, 'UTF-8')) {
                                $messageLength = $i;
                                break;
                            }
                        }
                        if ($messageLength !== null) {
                            $message = mb_substr($buffer, 0, $messageLength, '8bit');
                            if (mb_check_encoding($message, 'UTF-8')) {
                                if ($this->channel != $this->history_id) {
                                    $tmp .= $message;
                                    Redis::publish($this->channel, 'New ' . json_encode(['msg' => $message]));
                                    $buffer = mb_substr($buffer, $messageLength, null, '8bit');
                                } else {
                                    if (str_starts_with($message, '<') && !$cache) {
                                        $cache = true;
                                    }
                                    if (!$cache) {
                                        $tmp .= $message;
                                        $outputTmp = $tmp . '...';
                                        if ($kuwa_flag) {
                                            $outputTmp .= "\n\n[有關Kuwa的相關說明，請以 kuwaai.org 官網的資訊為準。]";
                                        }
                                        if ($warningMessages) {
                                            $outputTmp .= '<<<WARNING>>>' . implode("\n", $warningMessages) . '<<</WARNING>>>';
                                        }

                                Redis::publish($this->channel, 'New ' . json_encode(['msg' => $outputTmp]));
                            } else {
                                //start caching
                                $cached .= $message;
                                if (!(strpos('<<<WARNING>>>', $cached) !== false || strpos($cached, '<<<WARNING>>>') !== false)) {
                                    $cache = false;
                                    $tmp .= $cached;
                                    $outputTmp = $tmp;
                                    if ($this->channel == $this->history_id) {
                                        $outputTmp .= '...';
                                    }
                                    if ($kuwa_flag && $this->channel == $this->history_id) {
                                        $outputTmp .= "\n\n[有關Kuwa的相關說明，請以 kuwaai.org 官網的資訊為準。]";
                                    }
                                    if ($warningMessages) {
                                        $outputTmp .= '<<<WARNING>>>' . implode("\n", $warningMessages) . '<<</WARNING>>>';
                                    }

                                    if ($this->channel != $this->history_id) {
                                        // Loop over each character in the UTF-8 string
                                        for ($i = 0; $i < mb_strlen($outputTmp, 'UTF-8'); $i++) {
                                            // Get the current character
                                            $char = mb_substr($outputTmp, $i, 1, 'UTF-8');
                                            // Publish the character to Redis
                                            Redis::publish($this->channel, 'New ' . json_encode(['msg' => $char]));
                                        }
                                    } else {
                                        Redis::publish($this->channel, 'New ' . json_encode(['msg' => $outputTmp]));
                                    }
                                    $cached = '';
                                } elseif ($message === '>' && (str_ends_with($cached, '<<</WARNING>>>') || str_ends_with($cached, '<<<\/WARNING>>>'))) {
                                    $warningMessages[] = trim(str_replace(['<<<WARNING>>>', '<<</WARNING>>>', '<<<\/WARNING>>>'], '', $cached));
                                    $cache = false;
                                    $cached = '';
                                }
                            }
                        }
                        /*if (mb_strlen($tmp) > 3500) {
                            break;
                        }*/
                    }

                    if (trim($tmp) == '' && empty($warningMessages)) {
                        $tmp = '[Oops, the LLM returned empty message, please try again later or report to admins!]';
                    } else {
                        if ($this->channel != $this->history_id) {
                            Redis::publish($this->channel, 'Ended Ended');
                        } elseif ($kuwa_flag) {
                            $tmp .= "\n\n[有關Kuwa的相關說明，請以 kuwaai.org 官網的資訊為準。]";
                        }
                    }
                } catch (Exception $e) {
                    if ($this->channel != $this->history_id) {
                        $text = '\n[Sorry, something is broken, please try again later!]';
                        // Loop over each character in the UTF-8 string
                        for ($i = 0; $i < mb_strlen($text, 'UTF-8'); $i++) {
                            // Get the current character
                            $char = mb_substr($text, $i, 1, 'UTF-8');
                            // Publish the character to Redis
                            Redis::publish($this->channel, 'New ' . json_encode(['msg' => $char]));
                        }
                    } else {
                        Redis::publish($this->channel, 'New ' . json_encode(['msg' => $tmp . '\n[Sorry, something is broken, please try again later!]']));
                    }
                    $tmp .= "\n[Sorry, something is broken, please try again later!]";

                    Log::channel('analyze')->Debug('failJob ' . $this->history_id);
                } finally {
                    try {
                        if ($this->channel == $this->history_id) {
                            $history = Histories::find($this->history_id);
                            if ($history != null) {
                                $result = trim(preg_replace('#<<<WARNING>>>.*?<<</WARNING>>>#s', '', $tmp));
                                if ($warningMessages) {
                                    $result .= '<<<WARNING>>>' . implode("\n", $warningMessages) . '<<</WARNING>>>';
                                }
                                $history->fill(['msg' => $result]);
                                $history->save();
                                $tmp = $result;
                            }
                        }
                    } catch (Exception $e) {
                    }

                    $end = microtime(true);
                    $elapsed = $end - $start;
                    Log::channel('analyze')->Info('Out:' . $this->access_code . '|' . $this->user_id . '|' . $this->history_id . '|' . $elapsed . '|' . strlen(trim($tmp)) . '|' . Carbon::createFromFormat('Y-m-d H:i:s', $this->msgtime)->diffInSeconds(Carbon::now()) . '|' . $tmp);

                    if ($this->channel == $this->history_id) {
                        $msgTimeInSeconds = Carbon::createFromFormat('Y-m-d H:i:s', $this->msgtime)->timestamp;
                        $currentTimeInSeconds = Carbon::now()->timestamp;
                        $ExecutionTime = $currentTimeInSeconds - $msgTimeInSeconds;
                        if ($this->exit_when_finish) {
                            Redis::lrem(($this->channel == $this->history_id ? 'usertask_' : 'api_') . $this->user_id, 0, $this->history_id);
                        }
                        Redis::publish($this->channel, 'New ' . json_encode(['msg' => trim($tmp)]));
                        if ($this->exit_when_finish) {
                            Redis::publish($this->channel, 'Ended Ended');
                        }
                    } else {
                        Redis::lrem(($this->channel == $this->history_id ? 'usertask_' : 'api_') . $this->user_id, 0, $this->history_id);
                    }
                }
            }
        } catch (\Throwable $e) {
            Log::channel('analyze')->Info('Failed job: ' . $this->channel);
            Log::channel('analyze')->Info($e->getMessage());
            $history = Histories::find($this->history_id);
            if ($history != null) {
                $history->fill(['msg' => '[Sorry, something is broken, please try again later!]']);
                $history->save();
            }
            Redis::publish($this->channel, 'New ' . json_encode(['msg' => '[Sorry, something is broken, please try again later!]']));
            Redis::publish($this->channel, 'Ended Ended');
            Redis::lrem(($this->channel == $this->history_id ? 'usertask_' : 'api_') . $this->user_id, 0, $this->history_id);

            $msgTimeInSeconds = Carbon::createFromFormat('Y-m-d H:i:s', $this->msgtime)->timestamp;
            $currentTimeInSeconds = Carbon::now()->timestamp;
            $ExecutionTime = $currentTimeInSeconds - $msgTimeInSeconds;

            if ($ExecutionTime < 5) {
                sleep(5 - $ExecutionTime);
            }

            Redis::publish($this->channel, 'New ' . json_encode(['msg' => '[Sorry, something is broken, please try again later!]']));
            Redis::publish($this->channel, 'Ended Ended');
        }
    }
    public function failed(\Throwable $exception)
    {
        if ($this->channel == '') {
            $this->channel .= $this->history_id;
        }
        Log::channel('analyze')->Info('Failed job: ' . $this->channel);

        $history = Histories::find($this->history_id);
        if ($history != null) {
            $history->fill(['msg' => '[Sorry, something is broken, please try again later!]']);
            $history->save();
        }
        Redis::lrem(($this->channel == $this->history_id ? 'usertask_' : 'api_') . $this->user_id, 0, $this->history_id);

        Redis::publish($this->channel, 'New ' . json_encode(['msg' => '[Sorry, something is broken, please try again later!]']));
        Redis::publish($this->channel, 'Ended Ended');
    }
}

class Utf8Buffer
{
    private $buffer = '';

    /**
     * Adds a chunk of data to the buffer.
     *
     * @param string $chunk The data chunk to add.
     */
    public function addChunk(string $chunk): void
    {
        $this->buffer .= $chunk;
    }

    /**
     * Processes the buffer to extract and return complete UTF-8 messages.
     *  Returns null if no complete message is found.
     *
     * @return string|null The UTF-8 message, or null if none is found.
     */
    public function processBuffer(): ?string
    {
        $bufferLength = mb_strlen($this->buffer, '8bit');

        for ($i = $bufferLength; $i > 0; $i--) {
            $message = mb_substr($this->buffer, 0, $i, '8bit');

            // UTF-8 encoding check.
            if (mb_check_encoding($message, 'UTF-8')) {
                $this->buffer = mb_substr($this->buffer, $i, $bufferLength - $i, '8bit'); // remove the processed message from the buffer
                return $message;
            }
        }

        return ''; // No complete UTF-8 message found
    }

    /**
     * Gets the remaining unprocessed buffer.
     * @return string
     */
    public function getRemainingBuffer(): string
    {
        return $this->buffer;
    }
}
