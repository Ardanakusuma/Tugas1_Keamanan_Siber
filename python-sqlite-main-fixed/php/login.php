<?php
session_start();
include 'app.php';

// Jika sudah login, langsung arahkan ke index.php
if (isset($_SESSION['logged_in']) && $_SESSION['logged_in'] === true) {
    header('Location: index.php');
    exit;
}

// Proses login ketika form dikirim
if (isset($_POST['login'])) {
    $username = trim($_POST['username']);
    $password = trim($_POST['password']);

    // Contoh user statis (bisa diganti dengan tabel user di DB)
    $valid_user = "admin";
    $valid_pass = "1234";

    if ($username === $valid_user && $password === $valid_pass) {
        $_SESSION['logged_in'] = true;
        $_SESSION['username'] = $username;
        header('Location: index.php');
        exit;
    } else {
        $error = "Username atau password salah!";
    }
}
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Manajemen Siswa</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
    <h1>Login ke Sistem</h1>
    <form action="login.php" method="POST">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username" required>

        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required>

        <button type="submit" name="login">Masuk</button>
    </form>

    <?php if (isset($error)): ?>
        <p style="color:red;"><?php echo $error; ?></p>
    <?php endif; ?>
</div>
</body>
</html>
