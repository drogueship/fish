<html>
<body>
<table>
<?php
foreach (array_reverse(glob("*.wav")) as $filename) {
//echo "$filename<br>";
echo "<tr>";
echo "<td valign=\"middle\">$filename</td>";
echo "<td valign=\"middle\"><audio controls>";
echo "<source src=$filename type=\"audio/wav\">";
echo "</audio></td></tr>";
}
?>
</table>
</body>
</html>

