<?php
$package_name = $_SERVER['PATH_INFO'];
$package_name = str_replace('/','', $package_name);

function get_version($string) {
    $parts = explode('-', $string);
    return str_replace('.metadata', '', end($parts));
}

$files = glob('./metadata_files/' . $package_name . '*');

if (count($files) == 0) {
    http_response_code(404);
    exit;
}


$original_found_versions = array_map('get_version', $files);
natsort($original_found_versions);
$last_version = end($original_found_versions);


function make_array() {
    global $original_found_versions, $package_name, $version, $last_version;
    $output = '';
    foreach (array_slice($original_found_versions, 0, -1) as $version) {
        if (file_exists('./metadata_files/' . $package_name . '-' . $version . '.metadata')) {
            $output .= '    "' . $version . "\",\n";
        }
    }

    if (file_exists('./metadata_files/' . $package_name . '-' . $last_version . '.metadata')) {
        $output .= '    "' . $last_version . "\"\n";
    }
    
    return $output;
}

if (make_array() == '') {
    http_response_code(404);
    exit;
} else {
    echo "versions = [\n";
    echo make_array();
    echo "]\n";
    
    header('Content-type: text/plain');
}

?>