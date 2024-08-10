<?php
$package_name = $_SERVER['PATH_INFO'];
$package_name = str_replace('/','', $package_name);

function get_version($string) {
    $parts = explode('-', $string);
    return str_replace('.metadata', '', end($parts));
}

if (isset($_GET['version']) and !empty($_GET['version'])) {
    $version = $_GET['version']; 
} else {
    $version = 'latest';
}

$files = glob('./metadata_files/' . $package_name . '*');

if (count($files) == 0) {
    http_response_code(404);
    exit;
}

$original_found_versions = array_map('get_version', $files);
$GLOBALS['version_max_length'] = max(array_map('strlen', $original_found_versions));

function add_trailing_zeros($version) {
    $length = $GLOBALS['version_max_length'] - strlen($version);
    $version =  $version . str_repeat('.0', $length / 2);

    if (strlen($version) != $GLOBALS['version_max_length']) {
        $version .= '0';
    }
    
    return $version;
}

$found_versions = array_map('add_trailing_zeros', $original_found_versions);

try {
    if ($version == 'latest') {
        $version = max($found_versions);
    } elseif (strpos($version, '~') === 0) {
        $version = substr($version, 1);
        $temp_array = [];
        foreach ($found_versions as $vrs) {
            if (strpos($vrs, $version . '.') === 0 || $vrs == $version) {
                $temp_array[] = $vrs;
            }
        }
        $version = max($temp_array);
    } else {
        $version = add_trailing_zeros($version);
        if (strpos($version, '^') === 0) {
            $version = substr($version, 1);
            $version = max([$version, max($found_versions)]);
        } elseif (strpos($version, '_') === 0) {
            $version = substr($version, 1);
            $version = max([$version, min($found_versions)]);
        }
    }
} catch (\Throwable $th) {
    http_response_code(404);
    exit;
}

if (in_array($version, $found_versions)) {
    $version = $original_found_versions[array_search($version, $found_versions)];
} else {
    http_response_code(404);
    exit;
}

$filename = $package_name . '-' . $version . '.metadata';

if (file_exists('./metadata_files/' . $filename)) {
    echo file_get_contents('./metadata_files/' . $filename);
} else {
    http_response_code(404);
    exit;
}

header('Content-type: text/plain');

?>