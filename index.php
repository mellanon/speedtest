<?php
/*
    API Demo
 
    This script provides a RESTful API interface for a web application
 
    Input:
 
        $_GET['format'] = [ json | html | xml ]
        $_GET['method'] = []
 
    Output: A formatted HTTP response
 
    Author: Mark Roland
 
    History:
        11/13/2012 - Created
 
*/
 
// --- Step 1: Initialize variables and functions
 
/**
 * Deliver HTTP Response
 * @param string $format The desired HTTP response content type: [json, html, xml]
 * @param string $api_response The desired HTTP response data
 * @return void
 **/

#include_once('config.php');

function saveResult($deviceId, $sessionId, $timeCreated, $msg){
    $con=mysqli_connect("localhost","root","bitnami","speedtest");

    // Check connection
    if (mysqli_connect_errno()) {
        echo "Failed to connect to MySQL: " . mysqli_connect_error();
    }

    // escape variables for security
    $deviceId = mysqli_real_escape_string($con, $deviceId);
    $sessionId = mysqli_real_escape_string($con, $sessionId);
    $timeCreated = mysqli_real_escape_string($con, $timeCreated);
    $msg = mysqli_real_escape_string($con, $msg);
    $sql = "INSERT INTO result(deviceid, sessionid, msg, created) VALUES('$deviceId', '$sessionId', '$msg', '$timeCreated')";
    
    if (!mysqli_query($con,$sql)) {
        return false;
        die('Error: ' . mysqli_error($con));
    }

    mysqli_close($con);

    return true;
}

function getSpeedServerList($deviceId = 0, $deviceMac, $requestTime){
    $con=mysqli_connect("localhost","root","bitnami","speedtest");

    // Check connection
    if (mysqli_connect_errno()) {
        echo "Failed to connect to MySQL: " . mysqli_connect_error();
    }

    #TODO: Handle device identification based on both mac and deviceid
    #TODO: Time out settings from central storage or configuration file

    // escape variables for security
    $deviceId = mysqli_real_escape_string($con, $deviceId);
    $deviceMac = mysqli_real_escape_string($con, $deviceMac);
    $requestTime = mysqli_real_escape_string($con, $requestTime);
    $requestTime = date_create($requestTime);

    //Get request older than 4 minutes
    $sql = "SELECT rqid FROM request WHERE rqdeviceid = '$deviceId' AND EXTRACT(MINUTE FROM TIMEDIFF('$requestTime',rqcreated)) > 4"

    //Time out request older than 4 minutes
    $sql = "UPDATE request SET rqstatus = 4 WHERE rqid = "#value from above (loop) 
    
    //Log timeout 
    $sql = "INSERT INTO request_history(rqhrqid, rqhlog) VALUES('$rqid','Request timed out')"

    //Get requests in status new or in progress, newest first
    $sql = "SELECT * FROM request WHERE rqstatus < 3 AND rqdeviceid = '$deviceId' ORDER BY rqid DESC"

    //Store service order ID, bandwidth up/down of service
    #$serviceOrderId = 
    #$bandwidthDown =
    #$bandwidthUp = 

    //Get server list for current request
    $sql = "SELECT srvid FROM request INNER JOIN rsp_serverlist ON rqrspid = rsp_serverlist.rspslrspid INNER JOIN serverlist ON rsp_serverlist.rspslsrvid = serverlist.srvid WHERE rqid = '$rqid' ORDER BY serverlist.srvdistance ASC"

    if (!mysqli_query($con,$sql)) {
        return false;
        die('Error: ' . mysqli_error($con));
    }

    mysqli_close($con);

    //Log on request history that new config sent to device X

    //Return serviceOrderId, bandwidthDown, bandwidthUp, speedTestServerList[]

    return true;

}

function deliver_response($format, $api_response){
 
    // Define HTTP responses
    $http_response_code = array(
        200 => 'OK',
        400 => 'Bad Request',
        401 => 'Unauthorized',
        403 => 'Forbidden',
        404 => 'Not Found'
    );
 
    // Set HTTP Response
    header('HTTP/1.1 '.$api_response['status'].' '.$http_response_code[ $api_response['status'] ]);
 
    // Process different content types
    if( strcasecmp($format,'json') == 0 ){
 
        // Set HTTP Response Content Type
        header('Content-Type: application/json; charset=utf-8');
 
        // Format data into a JSON response
        $json_response = json_encode($api_response);
 
        // Deliver formatted data
        echo $json_response;
 
    }elseif( strcasecmp($format,'xml') == 0 ){
 
        // Set HTTP Response Content Type
        header('Content-Type: application/xml; charset=utf-8');
 
        // Format data into an XML response (This is only good at handling string data, not arrays)
        $xml_response = '<?xml version="1.0" encoding="UTF-8"?>'."\n".
            '<response>'."\n".
            "\t".'<code>'.$api_response['code'].'</code>'."\n".
            "\t".'<data>'.$api_response['data'].'</data>'."\n".
            '</response>';
 
        // Deliver formatted data
        echo $xml_response;
 
    }else{
 
        // Set HTTP Response Content Type (This is only good at handling string data, not arrays)
        header('Content-Type: text/html; charset=utf-8');
 
        // Deliver formatted data
        echo $api_response['data'];
 
    }
 
    // End script process
    exit;
 
}
 
// Define whether an HTTPS connection is required
$HTTPS_required = FALSE;
 
// Define whether user authentication is required
$authentication_required = FALSE;
 
// Define API response codes and their related HTTP response
$api_response_code = array(
    0 => array('HTTP Response' => 400, 'Message' => 'Unknown Error'),
    1 => array('HTTP Response' => 200, 'Message' => 'Success'),
    2 => array('HTTP Response' => 403, 'Message' => 'HTTPS Required'),
    3 => array('HTTP Response' => 401, 'Message' => 'Authentication Required'),
    4 => array('HTTP Response' => 401, 'Message' => 'Authentication Failed'),
    5 => array('HTTP Response' => 404, 'Message' => 'Invalid Request'),
    6 => array('HTTP Response' => 400, 'Message' => 'Invalid Response Format')
);
 
// Set default HTTP response of 'ok'
$response['code'] = 0;
$response['status'] = 404;
$response['data'] = NULL;
 
// --- Step 2: Authorization
 
// Optionally require connections to be made via HTTPS
if( $HTTPS_required && $_SERVER['HTTPS'] != 'on' ){
    $response['code'] = 2;
    $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
    $response['data'] = $api_response_code[ $response['code'] ]['Message'];
 
    // Return Response to browser. This will exit the script.
    deliver_response($_GET['format'], $response);
}
 
// Optionally require user authentication
if( $authentication_required ){
 
    if( empty($_POST['username']) || empty($_POST['password']) ){
        $response['code'] = 3;
        $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
        $response['data'] = $api_response_code[ $response['code'] ]['Message'];
 
        // Return Response to browser
        deliver_response($_GET['format'], $response);
 
    }
 
    // Return an error response if user fails authentication. This is a very simplistic example
    // that should be modified for security in a production environment
    elseif( $_POST['username'] != 'foo' && $_POST['password'] != 'bar' ){
        $response['code'] = 4;
        $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
        $response['data'] = $api_response_code[ $response['code'] ]['Message'];
 
        // Return Response to browser
        deliver_response($_GET['format'], $response);
 
    }
 
}
 
// --- Step 3: Process Request
 
// Method A: Say Hello to the API
if( strcasecmp($_GET['method'],'hello') == 0){
    $response['code'] = 1;
    $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
    $response['data'] = 'Hello World';
}

if($_SERVER['REQUEST_METHOD'] == "POST"){
    switch($_GET['method']){
        case "postResult":
            $data = json_decode($_POST['speedtest'],true);
            $deviceId = $data['deviceId'];
	    $timeCreated = $data['timeCreated'];
            $msg = $data['msg'];
	    $sessionId = $data['sessionId'];
            
#            $response['data'] = "!empty deviceId:".isset($deviceId)." timeCreated:".isset($timeCreated)." sessionId: ".isset($sessionId)." Message: ".isset($msg));
            if((isset($deviceId) && isset($timeCreated) && isset($msg) && isset($sessionId)) && saveResult($deviceId, $sessionId, $timeCreated, $msg)){
                $response['code'] = 1;
                $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
                $response['data'] = "Message created $timecreated from $devicdId has been saved";
            }else{
                $response['code'] = 5;
                $response['status'] = $api_response_code[ $response['code'] ]['HTTP Response'];
                $response['data'] .= 'Insufficient data provided to save the result.'.$_POST['speedtest'];           
	    }
        case "getSessionByMac":
            $data = json_decode($_POST['getSessionByMac'],true);

            $deviceId = $data['deviceId'];
            $macAddress = $data['mac'];
            $requestTime = date("Y-m-d H:i:s"); #Time when the function was called

            #Get active sessions for speed test device identified by deviceId or macAddress
            #Time out defined by difference between requestTime and sessionStartTime
            #Mark session as processing when sent off to client
            #Return serviceOrderId and array of speed test servers
        case "updateSessionState":
            #get device by mac or id
            #states; new, inprogress, completed, error

    }
}
 
// --- Step 4: Deliver Response
 
// Return Response to browser
deliver_response($_GET['format'], $response);
     
?>
