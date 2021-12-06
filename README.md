# midi2vjoy

It's a simple app with run on Windows only, but anyway gaming is only for windows right ?
The goal is to use a midi controller and convert it in a joypad (mainly for button), but you can maybe play platform 
game with it.

The best case scenario will be for a game witch require a lot of button, like car racing or flight simulator.

I tested it only with an x-touch mini from Behringer. If you want to have support your midi device, I would be happy to 
help, but I will need to have access to it (donation, amazon gift, or other).

This project is for everyone, but not every one will be able to make it run smoothly.
You will need some skill for it, you need to earn it.

   - install [vJoy](https://sourceforge.net/projects/vjoystick/) and configure it correctly for your needs
   - install [python](https://www.python.org/), add few modules, and know how to run a script
   - [json](https://www.json.org/) knowledge
   - a midi controller, and how to configure it

# midi controller

My x-touch mini is configured to behave like a keyboard, or drum, it plays a note on a tap of a button
For sure is not the default configuration, don't expect to make it work without configure yours

# vJoy config for x-touch mini

![vJoy conf for x-touch mini](./img/vJorConf.png)

# how to run and test it ?

For me the easiest way to run it is with pycharm, because I know this tool.

But basically you run it via a command line

like so : 
```
python.exe midi2vjoy.py --config ./xtouch-mini.json
```
full path is preferred, specially if you want to run it with un shortcut.

and testing it is easy with vJoy Monitor.

# json file

it's compose in 3 sections

  - input (string) 
  - output (string)
  - mappings (array)

```
{
  "input": "X-TOUCH MINI",
  "output": "X-TOUCH MINI",
  "mapping": [ 
  
  ]
}
```

## mapping

mapping is containing all mapping midi to vjoy

all mapping are defined with at least

  - channel (int)
  - control (int)
  - type (string)

```
 { "channel": 10, "control": 110, "type": "xxx", .... }
```

optional is the key "initial-value", it's useful for rotary

### pad / push 

on the type pad/push is mandatory to have a key "vjoy-btn"

  - vjoy-btn (int)

```
 { "channel": 10, "control": 110, "type": "pad", "vjoy-btn": 1 },
 { "channel": 10, "control": 91, "type": "push", "vjoy-btn": 17 }
```

### rotary

on the type rotary is mandatory to have 2 keys "vjoy-btn-dec" and "vjoy-btn-inc"

  - vjoy-btn-dec (int) when decrement
  - vjoy-btn-inc (int) when increment

optional is the key "activation_duration"
 
 - activation-duration (float) 

```
    { "channel": 10, "control": 101, "type": "rotary", "initial-value": 64, "vjoy-btn-dec": 27, "vjoy-btn-inc": 28},
    { "channel": 10, "control": 102, "type": "rotary", "initial-value": 64, "vjoy-btn-dec": 29, "vjoy-btn-inc": 30, "activation-duration": 0.02}
```

### slider/axis

on the type slider/axis is mandatory to have 1 keys "axis-name"

   - axis-name (string)
     - X
     - Y
     - Z
     - RX
     - RY
     - RZ
     - SL0
     - SL1
     - WHL
     - POV

```
    { "channel": 10, "control": 107, "type": "axis", "initial-value": 64, "axis-name": "Z"},
    { "channel": 10, "control": 90, "type": "slider", "axis-name": "SL0"}
```

