PREFIX := .compiled

.PHONY = all clean xclip pbcopy

all: game.hex

$(PREFIX)/map.8o $(PREFIX)/map_data.8o: Makefile generate-map.py assets/map.json
		./generate-map.py assets/map.json 3000 $(PREFIX)

$(PREFIX)/tiles.8o: Makefile ./generate-texture.py assets/*.png assets/tiles/*.png
		./generate-texture.py assets/tileset.png tileset 2 8 > $@
		./generate-texture.py --map2=3 assets/tiles/gems.png gem 2 8 >> $@
		./generate-texture.py --map2=3 assets/tiles/heart.png heart 2 8 >> $@
		./generate-texture.py --map1=3 assets/tiles/ninja.png ninja 2 8 >> $@
		./generate-texture.py assets/tiles/teleport.png teleport 2 16 >> $@
		./generate-texture.py --map1=2 --map2=3 --map0=1 assets/tiles/indicator.png indicator 2 8 >> $@
		./generate-texture.py assets/tiles/switch.png switch 2 8 >> $@
		./generate-texture.py assets/tiles/baby.png baby 2 16 >> $@
		./generate-texture.py assets/tiles/professor.png professor 2 8 >> $@
		./generate-texture.py assets/tiles/kiosk.png kiosk 2 8 >> $@
		./generate-texture.py --map2=3 assets/tiles/spikes.png spikes 2 8 >> $@
		./generate-texture.py assets/tiles/intro1.png intro1 2 16 >> $@
		./generate-texture.py assets/tiles/intro2.png intro2 2 16 >> $@
		./generate-texture.py assets/tiles/intro3.png intro3 2 16 >> $@
		./generate-texture.py --map2=3 assets/tiles/digits.png digits 2 8 >> $@
		./generate-texture.py --map1=3 assets/tiles/sorry-castle.png sorry_castle 2 16 >> $@
		./generate-texture.py --map2=3 assets/tiles/sorry-cloud.png sorry_cloud 2 16 >> $@


game.8o: \
	Makefile assets/* sources/*.8o sources/object/*.8o \
	$(PREFIX)/map_data.8o \
	$(PREFIX)/tiles.8o

		cat sources/main.8o > $@
		cat $(PREFIX)/map.8o >> $@
		cat sources/ninja.8o >> $@
		cat sources/objects.8o >> $@
		cat sources/utils.8o >> $@
		cat sources/map.8o >> $@
		cat sources/intro.8o >> $@
		cat sources/object/gem.8o >> $@
		cat sources/object/teleport.8o >> $@
		cat sources/object/switch.8o >> $@
		cat sources/object/indicator.8o >> $@
		cat sources/object/professor.8o >> $@
		cat sources/object/baby.8o >> $@
		cat sources/object/kiosk.8o >> $@
		cat sources/object/spikes.8o >> $@
		cat sources/object/baloon.8o >> $@
		cat $(PREFIX)/map_data.8o >> $@
		cat sources/sounds.8o >> $@
		echo ":org 0x6000" >> $@
		cat $(PREFIX)/tiles.8o >> $@

game.bin: game.8o
	./octo/octo game.8o $@

game.hex: game.bin ./generate-hex.py
	./generate-hex.py game.bin $@

xclip: game.hex
	cat game.hex | xclip

xclip-src: game.8o
	cat game.8o | xclip

pbcopy: game.hex
	cat game.hex | pbcopy

pbcopy-src: game.8o
	cat game.8o | pbcopy

clean:
		rm -f game.bin game.8o game.hex .compiled/*
