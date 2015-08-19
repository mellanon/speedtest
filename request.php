<?php
$saved = false;
if (isset($_GET['post'])){

    if (isset($_POST['name']) && isset($_POST['mac']) && isset($_POST['serviceorderid']) && isset($_POST['rsp']) && isset($_POST['status']) && isset($_POST['bwdown']) && isset($_POST['bwup']) && isset($_POST['created'])){

        $con=mysqli_connect("localhost","root","bitnami","speedtest");
        // Check connection
        if (mysqli_connect_errno()) {
            echo "Failed to connect to MySQL: " . mysqli_connect_error();
        }
        $name = mysqli_real_escape_string($con, $_POST['name']);
        $mac = mysqli_real_escape_string($con, $_POST['mac']);
        $serviceorderid = mysqli_real_escape_string($con, $_POST['serviceorderid']);
        $rsp = mysqli_real_escape_string($con, $_POST['rsp']);
        $status = mysqli_real_escape_string($con, $_POST['status']);
        $bwdown = mysqli_real_escape_string($con, $_POST['bwdown']);
        $bwup = mysqli_real_escape_string($con, $_POST['bwup']);
        $created = mysqli_real_escape_string($con, $_POST['created']);

        $sql = "INSERT INTO request (rqmac, rqserviceorderid, rqrspid, rqstatus, rqbwdown, rqbwup, rqcreated, rqname) VALUES('$mac', '$serviceorderid', '$rsp', '$status', '$bwdown', '$bwup', '$created', '$name')"; 
        if (!mysqli_query($con,$sql)) {
            $saved = false;
        }else{
            $saved = true;
        }

        mysqli_close($con);
    }else{
        $saved = false; //Some field is not set
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
<meta name="description" content="">
<meta name="author" content="">
<link rel="icon" href="../../favicon.ico">

<title>Speed Test Request</title>

<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

<!-- jQuery library -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>

<!-- Latest compiled JavaScript -->
<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

<!-- Custom styles for this template -->
<link href="bootstrap/css/signin.css" rel="stylesheet">

<!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
<!--[if lt IE 9]>
<script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
<script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
<![endif]-->
</head>

<body>

<div class="container">
<?php if($saved){?>
          <div class="alert alert-success text-center" role="alert">
        <strong>Speed Test Request Saved!</strong>
      </div>
<?php }?>
<form role="form" class="form-signin" action="request.php?post=1" method="post" id="speedtest">
    <div class="form-group">
        <h2>Speed Test Request</h2>
        <p>Use this form to create speed test requests which is required before you can initiate a speed test using the Northpower Speed Test Device!</p>
    </div>
  <div class="form-group">
    <label for="name">Customer Name:</label>
    <input type="text" class="form-control" id="name" value="Andreas" name="name">
  </div>
  <div class="form-group">
    <label for="mac">MAC address (00:0c:29:59:59:7b):</label>
    <input type="text" class="form-control" id="mac" value="00:0c:29:59:59:7b" autofocus required name="mac">
  </div>
  <div class="form-group">
    <label for="serviceorderid">Service Order ID:</label>
    <input type="text" class="form-control" id="serviceorderid" value="200074" name="serviceorderid">
  </div>
<div class="form-group">
  <label for="sel1">Service Provider:</label>
  <select class="form-control" id="rsp" name="rsp">
    <option value="0">None</option>
    <option value="1" selected>Spark</option>
    <option value="2">Vodafone</option>
    <option value="3">CallPlu</option>
  </select>
</div>
<div class="form-group">
  <label for="sel1">Request Status:</label>
  <select class="form-control" id="status" name="status">
    <option value="1">New</option>
    <option value="2">In Progress</option>
    <option value="3">Completed</option>
    <option value="4">Timed Out</option>
  </select>
</div>
  <div class="form-group">
    <label for="bwdown">Bandwidth Down (Mb/s):</label>
    <input type="text" class="form-control" id="bwdown" value="30" name="bwdown">
  </div>
  <div class="form-group">
    <label for="serviceorderid">Bandwidth Up (Mb/s):</label>
    <input type="text" class="form-control" id="bwup" value="10" name="bwup">
  </div>
  <div class="form-group">
    <label for="created">Created Date (request valid 5 minutes):</label>
    <input type="datetime" class="form-control" id="created" value="<?php echo date('Y-m-d H:i:s')?>" required name="created">
  </div>
  <button type="submit" class="btn btn-default">Submit</button>
</form>

<?php if($saved){?>
      <div class="alert alert-success text-center" role="alert">
        <strong>Speed Test Request Saved!</strong>
      </div>
<?php }?>


      <iframe src="index.php<?php if(isset($mac)){ echo '?mac=00:0c:29:59:59:7b'; }?>" style="zoom:0.60" width="100%" height="350" frameborder="0"></iframe>

</div> <!-- /container -->

<!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
<script src="bootstrap/js/ie10-viewport-bug-workaround.js"></script>
</body>
</html>


