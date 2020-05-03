echo "12" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio12/direction
while true; do
cat /sys/class/gpio/gpio12/value >> buttontest.txt
done
