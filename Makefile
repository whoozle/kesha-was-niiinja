PREFIX := .compiled

.PHONY = all clean xclip pbcopy

all: game.hex

$(PREFIX)/font.8o $(PREFIX)/font-data.8o: Makefile generate-font.py assets/font/5.font
		./generate-font.py assets/font/5.font font 1100 $(PREFIX)

$(PREFIX)/map.8o $(PREFIX)/map_data.8o: Makefile generate-map.py assets/map.json
		./generate-map.py assets/map.json 3000 $(PREFIX)

$(PREFIX)/tiles.8o: Makefile ./generate-texture.py assets/*.png assets/tiles/*.png
		./generate-texture.py assets/tileset.png tileset 2 8 > $@
		./generate-texture.py --map2=3 assets/tiles/gems.png gem 2 8 >> $@
		./generate-texture.py --map1=3 assets/tiles/ninja.png ninja 2 8 >> $@
		./generate-texture.py assets/tiles/teleport.png teleport 2 16 >> $@
		./generate-texture.py assets/tiles/indicator.png indicator 2 8 >> $@
		./generate-texture.py assets/tiles/switch.png switch 2 8 >> $@


game.8o: \
	Makefile assets/* sources/*.8o sources/object/*.8o \
	$(PREFIX)/font.8o $(PREFIX)/font_data.8o \
	$(PREFIX)/map_data.8o \
	$(PREFIX)/tiles.8o

		cat sources/main.8o > $@
		cat $(PREFIX)/map.8o >> $@
		cat sources/ninja.8o >> $@
		cat sources/objects.8o >> $@
		cat sources/utils.8o >> $@
		cat sources/map.8o >> $@
		cat sources/object/gem.8o >> $@
		cat sources/object/teleport.8o >> $@
		cat sources/object/switch.8o >> $@
		cat sources/object/indicator.8o >> $@
		cat $(PREFIX)/font.8o >> $@
		cat $(PREFIX)/map_data.8o >> $@
		cat $(PREFIX)/font_data.8o >> $@
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
