// C control code for modules
// manages sensor / actor interaction
// exposes receive_from/forward_to "skills" to be invoked by server-side module agents

#include "stdio.h"
#include "stdbool.h"

typedef enum
{
    forward = 1,
    no_translation = 0,
    backward = -1
} translation;

typedef enum
{
    clock_wise = 1,
    no_rotation = 0,
    counter_clock_wise = -1
} rotation;

typedef enum
{
    none = -1,
    receive_from = 1,
    forward_to = 2
} skill;
typedef enum
{
    left = 1,  // rot0 -> backward
    top = 2,   // rot90 -> backward
    right = 3, // rot0 -> forward
    bottom = 4 // rot90 -> forward
} direction;

typedef enum
{
    rot_0 = 0,
    rot_90 = 1
} rotation_state;

translation current_translation = no_translation;
rotation current_rotation = no_rotation;

skill current_skill = none;
direction target_direction = left;
rotation_state target_rotation_state = rot_0;

rotation_state current_rotation_state = rot_0;

bool ready_to_translate = false;

// extern Python // tbd: move to separate file for simple replacement by actual hardware implementations
bool _light_barrier();
bool _endlage_0();
bool _endlage_90();
void _set_rotation(int dir);
void _set_translation(int dir);
long _millis();
int _serial_read(); // byte or -1 if nothing to read
void _serial_write(int b);
void _log(char *message);
void _throw_exception();

// sensors + actors
bool light_barrier()
{
    return _light_barrier();
}

void set_translation(translation dir)
{
    current_translation = dir;
    _set_translation(dir);
}
void set_rotation(rotation dir)
{
    current_rotation = dir;
    _set_rotation(dir);
}

long millis()
{
    return _millis();
}

int command_2_skill_map[2] = {receive_from, forward_to};
int command_2_direction_map[4] = {left, top, right, bottom};
int direction_2_target_rotation_state_map[4] = {rot_0, rot_90, rot_0, rot_90};

void read_command()
{
    int read = _serial_read();
    if (read == -1)
    {
        return;
    }
    // 0 -> receive, left
    // 1 -> receive, top
    // 2 -> receive, right
    // 3 -> receive, bottom
    // 4 -> forward, left
    // 5 -> forward, top
    // 6 -> forward, right
    // 7 -> forward, bottom
    if(read > 7){
        _log("ERROR: Command > 7");
        return;
    }
    current_skill = command_2_skill_map[read >= 4];
    target_direction = command_2_direction_map[read % 4];
    target_rotation_state = direction_2_target_rotation_state_map[target_direction - 1];
    ready_to_translate = false;
    _log("starting skill..");
}

void turn_to_target_direction()
{
    if (current_rotation != no_rotation)
    {
        // have we arrived yet?
        if (((target_rotation_state == rot_0) && _endlage_0()) ||
            ((target_rotation_state == rot_90) && _endlage_90()))
        {
            set_rotation(no_rotation);
            current_rotation_state = target_rotation_state;
        }
        return;
    }
    // start rotation
    _log("starting rotation..");
    if (target_rotation_state == rot_90)
    {
        set_rotation(clock_wise);
        return;
    }
    if (target_rotation_state == rot_0)
    {
        set_rotation(counter_clock_wise);
        return;
    }
}

void start_translation()
{
    _log("staring to translate..");
    if ((target_direction == right) || (target_direction == bottom))
    {
        if (current_skill == forward_to)
            set_translation(forward);
        else
            set_translation(backward);
        return;
    }
    if ((target_direction == left) || (target_direction == top))
    {
        if (current_skill == forward_to)
            set_translation(backward);
        else
            set_translation(forward);
        return;
    }
}

void check_done()
{
    if (current_skill == forward_to)
    {
        int read = _serial_read();
        if (read != -1)
        {
            set_translation(no_translation);
            current_skill = none;
            _log("skill done. (forward)");
        }
        return;
    }
    if (current_skill == receive_from)
    {
        if (light_barrier())
        {
            set_translation(no_translation);
            current_skill = none;
            _serial_write(10);
            _log("skill done. (receive)");
        }
        return;
    }
}

void translate()
{
    if (current_translation != no_translation)
    {
        check_done();
        return;
    }
    start_translation();
}

void get_ready_to_translate()
{
    if (current_skill == receive_from)
    {
        _serial_write(10);          // confirm readiness to receipt once
        ready_to_translate = true; // proceed immediately
    }
    if (current_skill == forward_to)
    {
        if (_serial_read() != -1) // wait for confirmation to start translation
        {
            ready_to_translate = true; // proceed after confirmation
        }
    }
}

void setup()
{
}

void loop() // tbd: loop -> called on interrupt for sensors+communication?
{
    // 0. wait for command to activate skill
    if (current_skill == none)
    {
        read_command(); // wait for new command to be set
        return;
    }

    // 1. get into correct direction
    if (current_rotation_state != target_rotation_state)
    {
        turn_to_target_direction();
        return;
    }

    // 2. communicate readiness to receive / wait for command to start translation!
    if (!ready_to_translate)
    {
        get_ready_to_translate();
        return;
    }

    // 3. translate until done
    translate();
}
