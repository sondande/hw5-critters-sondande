#!/usr/bin/env python3

import argparse
import critter
import critter_model
import critter_gui
import inspect
import os
import threading

#import tiger, elephant, stone, mouse, chameleon
#STANDARD_CRITTERS = (tiger.Tiger, elephant.Elephant, stone.Stone, mouse.Mouse, chameleon.Chameleon)
STANDARD_CRITTERS = ()


def get_critters(directory='.'):
    """
    Finds all critter definitions in the given directory and returns them
    as a list of class objects. Only classes which subclass our Critter
    will be included.
    """
    files = filter(lambda x: x.endswith('.py'), os.listdir(directory))
    modules = map(lambda x: x[:-3], files)
    critters = []
    for module in modules:
        exec('import %s' % module)
        for name, obj in inspect.getmembers(eval(module)):
            # This should use issubclass(obj, Critter), but that doesn't work
            # for reasons I don't understand. Provided nobody decides to create
            # a non-Critter class which has a getMove method, we're fine.
            if inspect.isclass(obj) and hasattr(obj, 'getMove'):
                critters.append(obj)
    critters.remove(critter.Critter)
    return critters

def populate_model(model):
    for standard in STANDARD_CRITTERS:
        model.add(standard, 25)

def format_results(results):
    "Returns the results of a critter fight in a nice format."
    return '\n'.join(['%s:%20s wins %3s alive %3s total %3s health %3s karma' % (critter.__name__, state.wins, state.alive, state.wins + state.alive, state.health, state.karma)
                      for critter, state in results])

def quickfight(critter1, critter2, iterations=1000):
    """
    Fight critter1 and critter2 with the standard classes,
    without showing a GUI. Prints the results at the end.
    """
    c = critter_model.CritterModel(50, 40, threading.Lock())
    populate_model(c)
    c.add(critter1, 25)
    c.add(critter2, 25)
    for i in range(iterations):
        c.update()
    print(format_results(c.results()))

def showfight(critter1, critter2):
    """
    Fight critter1 and critter2 with the standard classes, with a
    GUI. Prints the results at the end.
    """
    c = critter_model.CritterModel(50, 40, threading.Lock())
    populate_model(c)
    c.add(critter1, 25)
    c.add(critter2, 25)
    gui = critter_gui.CritterGUI(c)
    gui.start()

def get_class(crittername, critterlist):
    """
    Returns the string name of a critter into the actual class
    object, if it's in critterlist. Otherwise return None.
    """
    for c in critterlist:
        if c.__name__ == crittername:
            return c
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quickfight', nargs=2, required=False)
    parser.add_argument('--fight', nargs=2, required=False)
    args = parser.parse_args()
    critters = get_critters()
    if args.quickfight:
        critter1 = get_class(args.quickfight[0], critters)
        critter2 = get_class(args.quickfight[1], critters)
        quickfight(critter1, critter2)
    elif args.fight:
        critter1 = get_class(args.fight[0], critters)
        critter2 = get_class(args.fight[1], critters)
        showfight(critter1, critter2)
    else:
        model = critter_model.CritterModel(70, 40, threading.Lock())
        #populate_model(c)
        for critter in critters:
            model.add(critter, 25)
        c = critter_gui.CritterGUI(model)
        input()
    
if __name__ == '__main__':
    main()
