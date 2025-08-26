FRUIT=$1
IF [ $FRUIT == APPLE]; then
	echo "You selected Apple!"
elif [ $FRUIT == ORANGE ]; then
	echo "You selected Orange!"
elif [ $FRUIT == GRAPE ]; then
	echo "YOU Selected Grape!"
else
	echo "You selected other Fruit!"
fi
