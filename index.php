<?php
if (isset($_GET['mac'])){
    $mac = $_GET['mac'];
}else{
    $mac = null;
}

?>

<!DOCTYPE HTML>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8" />
    <title>JSON-RPC Demo for JQuery Terminal Emulator</title>
    <meta name="author" content="Jakub Jankiewicz - jcubic&#64;onet.pl"/>
    <meta name="Description" content="Demonstration for JQuery Terminal Emulator using call automaticly JSON-RPC service (in php) with authentication."/>
    <link rel="sitemap" type="application/xml" title="Sitemap" href=""/>
    <link rel="shortcut icon" href="favicon.ico"/>
    <script src="js/jquery-1.7.1.min.js"></script>
    <script src="js/jquery.mousewheel-min.js"></script>
    <script src="js/jquery.terminal-min.js"></script>
    <link href="css/jquery.terminal.css" rel="stylesheet"/>
  </head>
<body>

<script>
var current_id = 0
var last_id = 0
var refresher = 0

// global placeholder for term object
var terminal = null;

jQuery(function($) {
  $('html').terminal(function(cmd, term) {
          terminal = term; //global reference
          clearInterval(refresher);
          term.pause();
          //$.jrpc is helper function which
          //creates json-rpc request
          refresher = setInterval(function(){
          $.jrpc("mysql-rpc-demo.php",
            "query",
            [cmd],
            function(data) {
              term.resume();
              if (data.error) {
                term.error(data.error.message);
              } else {
                if (typeof data.result == 'boolean') {
                  term.echo(data.result ?
                            'success' :
                            'fail');
                } else {
                  len = data.result.length;
                    term.clear();
                    term.echo("R  | D | Device MAC        | SOID   | Timestamp           | Log Message");
                    for(var i=0;i<len; ++i) {
                      var s = data.result[i].join(' | ');
		      s = s.replace(/(?:\r\n|\r|\n)/g, '');
                      //s = s.replace(/.*\w.*/g,'');
                      term.echo(s);
                    }
                   
                }
              }
            },
            function(xhr, status, error) {
              term.error('[AJAX] ' + status +
                         ' - Server reponse is: \n' +
                         xhr.responseText + 'test ' + error);
                         term.resume();
                   }); // rpc call
          },5000);
          }, {
              greetings: "Listen to speed test results from the specified device",
<?php if(!is_null($mac)){?>
            onInit: function(terminal) {
                window.terminal = terminal;
                terminal.exec('<?php echo $mac?>');
            },
<?php }?>
            prompt: "DeviceID> "});
       });
</script>
</body>
