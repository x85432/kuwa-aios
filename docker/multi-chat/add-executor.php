<?php

# A backdoor API to add executor using FastCGI.
# [Warning] This API should not be exposed to the Internet.

$access_code = escapeshellarg($_POST["access_code"]);
$name = escapeshellarg($_POST["name"]);
$create_bot = escapeshellarg($_POST["create_bot"]);
$image = "";
if (isset($_POST["image"])){
    $image = '/app/public/images/' . $_POST["image"];
    $image = "--image=".escapeshellarg($image);
}
$do_not_create_bot = "";
if (isset($_POST["create_bot"]) && (strtolower($_POST["create_bot"]) == "false")) {
  $do_not_create_bot = "--do_not_create_bot";
} 

$cmd = sprintf("php /app/artisan model:config %s %s %s %s 2>&1", $access_code, $name, $image, $do_not_create_bot);
exec($cmd, $output, $retval);
echo "Returned with status $retval and output:\n";
print_r($output);