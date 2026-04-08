> ## Documentation Index
> Fetch the complete documentation index at: https://docs.comfy.org/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

Custom nodes allow you to implement new features and share them with the wider community.

A custom node is like any Comfy node: it takes input, does something to it, and produces an output.
While some custom nodes perform highly complex tasks, many just do one thing. Here's an example of a
simple node that takes an image and inverts it.

<img src="https://mintcdn.com/dripart/NmGUk_QSXQXRVtZP/images/invert_image_node.png?fit=max&auto=format&n=NmGUk_QSXQXRVtZP&q=85&s=8088073e29e8af1bc700937ecb3b77e9" alt="Unique Images Node" width="564" height="279" data-path="images/invert_image_node.png" />

Custom node examples：

* [cookiecutter-comfy-extension](https://github.com/Comfy-Org/cookiecutter-comfy-extension)
* [ComfyUI-React-Extension-Template](https://github.com/Comfy-Org/ComfyUI-React-Extension-Template)
* [ComfyUI\_frontend\_vue\_basic](https://github.com/jtydhr88/ComfyUI_frontend_vue_basic)

## Client-Server Model

Comfy runs in a client-server model. The server, written in Python, handles all the real work: data-processing, models, image diffusion etc. The client, written in Javascript, handles the user interface.

Comfy can also be used in API mode, in which a workflow is sent to the server by a non-Comfy client (such as another UI, or a command line script).

Custom nodes can be placed into one of four categories:

### Server side only

The majority of Custom Nodes run purely on the server side, by defining a Python class that specifies the input and output types, and provides a function that can be called to process inputs and produce an output.

### Client side only

A few Custom Nodes provide a modification to the client UI, but do not add core functionality. Despite the name, they may not even add new nodes to the system.

### Independent Client and Server

Custom nodes may provide additional server features, and additional (related) UI features (such as a new widget to deal with a new data type). In most cases, communication between the client and server can be handled by the Comfy data flow control.

### Connected Client and Server

In a small number of cases, the UI features and the server need to interact with each other directly.

<Warning>Any node that requires Client-Server communication will not be compatible with use through the API.</Warning>










# Getting Started

This page will take you step-by-step through the process of creating a custom node.

Our example will take a batch of images, and return one of the images. Initially, the node
will return the image which is, on average, the lightest in color; we'll then extend
it to have a range of selection criteria, and then finally add some client side code.

This page assumes very little knowledge of Python or Javascript.

After this walkthrough, dive into the details of [backend code](./backend/server_overview), and
[frontend code](./backend/server_overview).

## Write a basic node

### Prerequisites

* A working ComfyUI [installation](/installation/manual_install). For development, we recommend installing ComfyUI manually.
* A working comfy-cli [installation](/comfy-cli/getting-started).

### Setting up

```bash  theme={null}
cd ComfyUI/custom_nodes
comfy node scaffold
```

After answering a few questions, you'll have a new directory set up.

```bash  theme={null}
 ~  % comfy node scaffold
You've downloaded .cookiecutters/cookiecutter-comfy-extension before. Is it okay to delete and re-download it? [y/n] (y): y
  [1/9] full_name (): Comfy
  [2/9] email (you@gmail.com): me@comfy.org
  [3/9] github_username (your_github_username): comfy
  [4/9] project_name (My Custom Nodepack): FirstComfyNode
  [5/9] project_slug (firstcomfynode): 
  [6/9] project_short_description (A collection of custom nodes for ComfyUI): 
  [7/9] version (0.0.1): 
  [8/9] Select open_source_license
    1 - GNU General Public License v3
    2 - MIT license
    3 - BSD license
    4 - ISC license
    5 - Apache Software License 2.0
    6 - Not open source
    Choose from [1/2/3/4/5/6] (1): 1
  [9/9] include_web_directory_for_custom_javascript [y/n] (n): y
Initialized empty Git repository in firstcomfynode/.git/
✓ Custom node project created successfully!
```

### Defining the node

Add the following code to the end of `src/nodes.py`:

```Python src/nodes.py theme={null}
class ImageSelector:
    CATEGORY = "example"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "choose_image"
```

<Info>The basic structure of a custom node is described in detail [here](/custom-nodes/backend/server_overview). </Info>

A custom node is defined using a Python class, which must include these four things: `CATEGORY`,
which specifies where in the add new node menu the custom node will be located,
`INPUT_TYPES`, which is a class method defining what inputs the node will take
(see [later](/custom-nodes/backend/server_overview#input-types) for details of the dictionary returned),
`RETURN_TYPES`, which defines what outputs the node will produce, and `FUNCTION`, the name
of the function that will be called when the node is executed.

<Tip>Notice that the data type for input and output is `IMAGE` (singular) even though
we expect to receive a batch of images, and return just one. In Comfy, `IMAGE` means
image batch, and a single image is treated as a batch of size 1.</Tip>

### The main function

The main function, `choose_image`, receives named arguments as defined in `INPUT_TYPES`, and
returns a `tuple` as defined in `RETURN_TYPES`. Since we're dealing with images, which are internally
stored as `torch.Tensor`,

```Python  theme={null}
import torch
```

Then add the function to your class. The datatype for image is `torch.Tensor` with shape `[B,H,W,C]`,
where `B` is the batch size and `C` is the number of channels - 3, for RGB. If we iterate over such
a tensor, we will get a series of `B` tensors of shape `[H,W,C]`. The `.flatten()` method turns
this into a one dimensional tensor, of length `H*W*C`, `torch.mean()` takes the mean, and `.item()`
turns a single value tensor into a Python float.

```Python  theme={null}
def choose_image(self, images):
    brightness = list(torch.mean(image.flatten()).item() for image in images)
    brightest = brightness.index(max(brightness))
    result = images[brightest].unsqueeze(0)
    return (result,)
```

Notes on those last two lines:

* `images[brightest]` will return a Tensor of shape `[H,W,C]`. `unsqueeze` is used to insert a (length 1) dimension at, in this case, dimension zero, to give
  us `[B,H,W,C]` with `B=1`: a single image.
* in `return (result,)`, the trailing comma is essential to ensure you return a tuple.

### Register the node

To make Comfy recognize the new node, it must be available at the package level. Modify the `NODE_CLASS_MAPPINGS` variable at the end of `src/nodes.py`. You must restart ComfyUI to see any changes.

```Python src/nodes.py theme={null}

NODE_CLASS_MAPPINGS = {
    "Example" : Example,
    "Image Selector" : ImageSelector,
}

# Optionally, you can rename the node in the `NODE_DISPLAY_NAME_MAPPINGS` dictionary.
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "Image Selector": "Image Selector",
}
```

<Info>For a detailed explanation of how ComfyUI discovers and loads custom nodes, see the [node lifecycle documentation](/custom-nodes/backend/lifecycle).</Info>

## Add some options

That node is maybe a bit boring, so we might add some options; a widget that allows you to
choose the brightest image, or the reddest, bluest, or greenest. Edit your `INPUT_TYPES` to look like:

```Python  theme={null}
@classmethod    
def INPUT_TYPES(s):
    return { "required":  { "images": ("IMAGE",), 
                            "mode": (["brightest", "reddest", "greenest", "bluest"],)} }
```

Then update the main function. We'll use a fairly naive definition of 'reddest' as being the average
`R` value of the pixels divided by the average of all three colors. So:

```Python  theme={null}
def choose_image(self, images, mode):
    batch_size = images.shape[0]
    brightness = list(torch.mean(image.flatten()).item() for image in images)
    if (mode=="brightest"):
        scores = brightness
    else:
        channel = 0 if mode=="reddest" else (1 if mode=="greenest" else 2)
        absolute = list(torch.mean(image[:,:,channel].flatten()).item() for image in images)
        scores = list( absolute[i]/(brightness[i]+1e-8) for i in range(batch_size) )
    best = scores.index(max(scores))
    result = images[best].unsqueeze(0)
    return (result,)
```

## Tweak the UI

Maybe we'd like a bit of visual feedback, so let's send a little text message to be displayed.

### Send a message from server

This requires two lines to be added to the Python code:

```Python  theme={null}
from server import PromptServer
```

and, at the end of the `choose_image` method, add a line to send a message to the front end (`send_sync` takes a message
type, which should be unique, and a dictionary)

```Python  theme={null}
PromptServer.instance.send_sync("example.imageselector.textmessage", {"message":f"Picked image {best+1}"})
return (result,)
```

### Write a client extension

To add some Javascript to the client, create a subdirectory, `web/js` in your custom node directory, and modify the end of `__init__.py`
to tell Comfy about it by exporting `WEB_DIRECTORY`:

```Python  theme={null}
WEB_DIRECTORY = "./web/js"
__all__ = ['NODE_CLASS_MAPPINGS', 'WEB_DIRECTORY']
```

The client extension is saved as a `.js` file in the `web/js` subdirectory, so create `image_selector/web/js/imageSelector.js` with the
code below. (For more, see [client side coding](./js/javascript_overview)).

```Javascript  theme={null}
import { app } from "../../scripts/app.js";
app.registerExtension({
	name: "example.imageselector",
    async setup() {
        function messageHandler(event) { alert(event.detail.message); }
        app.api.addEventListener("example.imageselector.textmessage", messageHandler);
    },
})
```

All we've done is register an extension and add a listener for the message type we are sending in the `setup()` method. This reads the dictionary we sent (which is stored in `event.detail`).

Stop the Comfy server, start it again, reload the webpage, and run your workflow.

### The complete example

The complete example is available [here](https://gist.github.com/robinjhuang/fbf54b7715091c7b478724fc4dffbd03). You can download the example workflow [JSON file](https://github.com/Comfy-Org/docs/blob/main/public/workflow.json) or view it below:

<div align="center">
  <img src="https://mintcdn.com/dripart/EgZuQyCGLVUEw53Z/images/firstnodeworkflow.png?fit=max&auto=format&n=EgZuQyCGLVUEw53Z&q=85&s=a6f6c26f0dba136f864c59044909c55c" alt="Image Selector Workflow" width="100%" data-path="images/firstnodeworkflow.png" />
</div>












# Properties

> Properties of a custom node

### Simple Example

Here's the code for the Invert Image Node, which gives an overview of the key concepts in custom node development.

```python  theme={null}
class InvertImageNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { "image_in" : ("IMAGE", {}) },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image_out",)
    CATEGORY = "examples"
    FUNCTION = "invert"

    def invert(self, image_in):
        image_out = 1 - image_in
        return (image_out,)
```

### Main properties

Every custom node is a Python class, with the following key properties:

#### INPUT\_TYPES

`INPUT_TYPES`, as the name suggests, defines the inputs for the node. The method returns a `dict`
which *must* contain the key `required`, and *may* also include the keys `optional` and/or `hidden`. The only difference
between `required` and `optional` inputs is that `optional` inputs can be left unconnected.
For more information on `hidden` inputs, see [Hidden Inputs](./more_on_inputs#hidden-inputs).

Each key has, as its value, another `dict`, in which key-value pairs specify the names and types of the inputs.
The types are defined by a `tuple`, the first element of which defines the data type,
and the second element of which is a `dict` of additional parameters.

Here we have just one required input, named `image_in`, of type `IMAGE`, with no additional parameters.

Note that unlike the next few attributes, this `INPUT_TYPES` is a `@classmethod`. This is so
that the options in dropdown widgets (like the name of the checkpoint to be loaded) can be
computed by Comfy at run time. We'll go into this more later. {/* TODO link when written */}

#### RETURN\_TYPES

A `tuple` of `str` defining the data types returned by the node.
If the node has no outputs this must still be provided `RETURN_TYPES = ()`
<Warning>If you have exactly one output, remember the trailing comma: `RETURN_TYPES = ("IMAGE",)`.
This is required for Python to make it a `tuple`</Warning>

#### RETURN\_NAMES

The names to be used to label the outputs. This is optional; if omitted, the names are simply the `RETURN_TYPES` in lowercase.

#### CATEGORY

Where the node will be found in the ComfyUI **Add Node** menu. Submenus can be specified as a path, eg. `examples/trivial`.

#### FUNCTION

The name of the Python function in the class that should be called when the node is executed.

The function is called with named arguments. All `required` (and `hidden`) inputs will be included;
`optional` inputs will be included only if they are connected, so you should provide default values for them in the function
definition (or capture them with `**kwargs`).

The function returns a tuple corresponding to the `RETURN_TYPES`. This is required even if nothing is returned (`return ()`).
Again, if you only have one output, remember that trailing comma `return (image_out,)`!

### Execution Control Extras

A great feature of Comfy is that it caches outputs,
and only executes nodes that might produce a different result than the previous run.
This can greatly speed up lots of workflows.

In essence this works by identifying which nodes produce an output (these, notably the Image Preview and Save Image nodes, are always executed), and then working
backwards to identify which nodes provide data that might have changed since the last run.

Two optional features of a custom node assist in this process.

#### OUTPUT\_NODE

By default, a node is not considered an output. Set `OUTPUT_NODE = True` to specify that it is.

#### IS\_CHANGED

By default, Comfy considers that a node has changed if any of its inputs or widgets have changed.
This is normally correct, but you may need to override this if, for instance, the node uses a random
number (and does not specify a seed - it's best practice to have a seed input in this case so that
the user can control reproducibility and avoid unnecessary execution), or loads an input that may have
changed externally, or sometimes ignores inputs (so doesn't need to execute just because those inputs changed).

<Warning>Despite the name, IS\_CHANGED should not return a `bool`</Warning>

`IS_CHANGED` is passed the same arguments as the main function defined by `FUNCTION`, and can return any
Python object. This object is compared with the one returned in the previous run (if any) and the node
will be considered to have changed if `is_changed != is_changed_old` (this code is in `execution.py` if you need to dig).

Since `True == True`, a node that returns `True` to say it has changed will be considered not to have! I'm sure this would
be changed in the Comfy code if it wasn't for the fact that it might break existing nodes to do so.

To specify that your node should always be considered to have changed (which you should avoid if possible, since it
stops Comfy optimising what gets run), `return float("NaN")`. This returns a `NaN` value, which is not equal
to anything, even another `NaN`.

A good example of actually checking for changes is the code from the built-in LoadImage node, which loads the image and returns a hash

```python  theme={null}
    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()
```

#### SEARCH\_ALIASES

Optional. A list of alternative names users might search for when looking for this node.
This is included in the `/object_info` API response as `search_aliases`.

```python  theme={null}
SEARCH_ALIASES = ["text concat", "join text", "merge strings"]
```

### Other attributes

There are three other attributes that can be used to modify the default Comfy treatment of a node.

#### INPUT\_IS\_LIST, OUTPUT\_IS\_LIST

These are used to control sequential processing of data, and are described [later](./lists).

### VALIDATE\_INPUTS

If a class method `VALIDATE_INPUTS` is defined, it will be called before the workflow begins execution.
`VALIDATE_INPUTS` should return `True` if the inputs are valid, or a message (as a `str`) describing the error (which will prevent execution).

#### Validating Constants

<Warning>Note that `VALIDATE_INPUTS` will only receive inputs that are defined as constants within the workflow. Any inputs that are received from other nodes will *not* be available in `VALIDATE_INPUTS`.</Warning>

`VALIDATE_INPUTS` is called with only the inputs that its signature requests (those returned by `inspect.getfullargspec(obj_class.VALIDATE_INPUTS).args`). Any inputs which are received in this way will *not* run through the default validation rules. For example, in the following snippet, the front-end will use the specified `min` and `max` values of the `foo` input, but the back-end will not enforce it.

```python  theme={null}
class CustomNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { "foo" : ("INT", {"min": 0, "max": 10}) },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, foo):
        # YOLO, anything goes!
        return True
```

Additionally, if the function takes a `**kwargs` input, it will receive *all* available inputs and all of them will skip validation as if specified explicitly.

#### Validating Types

If the `VALIDATE_INPUTS` method receives an argument named `input_types`, it will be passed a dictionary in which the key is the name of each input which is connected to an output from another node and the value is the type of that output.

When this argument is present, all default validation of input types is skipped. Here's an example making use of the fact that the front-end allows for the specification of multiple types:

```python  theme={null}
class AddNumbers:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input1" : ("INT,FLOAT", {"min": 0, "max": 1000})
                "input2" : ("INT,FLOAT", {"min": 0, "max": 1000})
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        # The min and max of input1 and input2 are still validated because
        # we didn't take `input1` or `input2` as arguments
        if input_types["input1"] not in ("INT", "FLOAT"):
            return "input1 must be an INT or FLOAT type"
        if input_types["input2"] not in ("INT", "FLOAT"):
            return "input2 must be an INT or FLOAT type"
        return True
```











# Lifecycle

## How Comfy loads custom nodes

When Comfy starts, it scans the directory `custom_nodes` for Python modules, and attempts to load them.
If the module exports `NODE_CLASS_MAPPINGS`, it will be treated as a custom node.
<Tip>A python module is a directory containing an `__init__.py` file.
The module exports whatever is listed in the `__all__` attribute defined in `__init__.py`.</Tip>

### **init**.py

`__init__.py` is executed when Comfy attempts to import the module. For a module to be recognized as containing
custom node definitions, it needs to export `NODE_CLASS_MAPPINGS`. If it does (and if nothing goes wrong in the import),
the nodes defined in the module will be available in Comfy. If there is an error in your code,
Comfy will continue, but will report the module as having failed to load. So check the Python console!

A very simple `__init__.py` file would look like this:

```python  theme={null}
from .python_file import MyCustomNode
NODE_CLASS_MAPPINGS = { "My Custom Node" : MyCustomNode }
__all__ = ["NODE_CLASS_MAPPINGS"]
```

#### NODE\_CLASS\_MAPPINGS

`NODE_CLASS_MAPPINGS` must be a `dict` mapping custom node names (unique across the Comfy install)
to the corresponding node class.

#### NODE\_DISPLAY\_NAME\_MAPPINGS

`__init__.py` may also export `NODE_DISPLAY_NAME_MAPPINGS`, which maps the same unique name to a display name for the node.
If `NODE_DISPLAY_NAME_MAPPINGS` is not provided, Comfy will use the unique name as the display name.

#### WEB\_DIRECTORY

If you are deploying client side code, you will also need to export the path, relative to the module, in which the
JavaScript files are to be found. It is conventional to place these in a subdirectory of your custom node named `js`.
<Tip>*Only* `.js` files will be served; you can't deploy `.css` or other types in this way</Tip>

<Warning>In previous versions of Comfy, `__init__.py` was required to copy the JavaScript files into the main Comfy web
subdirectory. You will still see code that does this. Don't.</Warning>










# Datatypes

These are the most important built in datatypes. You can also [define your own](./more_on_inputs#custom-datatypes).

Datatypes are used on the client side to prevent a workflow from passing the wrong form of data into a node - a bit like strong typing.
The JavaScript client side code will generally not allow a node output to be connected to an input of a different datatype,
although a few exceptions are noted below.

## Comfy datatypes

### COMBO

* No additional parameters in `INPUT_TYPES`

* Python datatype: defined as `list[str]`, output value is `str`

Represents a dropdown menu widget.
Unlike other datatypes, `COMBO` it is not specified in `INPUT_TYPES` by a `str`, but by a `list[str]`
corresponding to the options in the dropdown list, with the first option selected by default.

`COMBO` inputs are often dynamically generated at run time. For instance, in the built-in `CheckpointLoaderSimple` node, you find

```
"ckpt_name": (folder_paths.get_filename_list("checkpoints"), )
```

or they might just be a fixed list of options,

```
"play_sound": (["no","yes"], {}),
```

### Primitive and reroute

Primitive and reroute nodes only exist on the client side. They do not have an intrinsic datatype, but when connected they take on
the datatype of the input or output to which they have been connected (which is why they can't connect to a `*` input...)

## Python datatypes

### INT

* Additional parameters in `INPUT_TYPES`:

  * `default` is required

  * `min` and `max` are optional

* Python datatype `int`

### FLOAT

* Additional parameters in `INPUT_TYPES`:

  * `default` is required

  * `min`, `max`, `step` are optional

* Python datatype `float`

### STRING

* Additional parameters in `INPUT_TYPES`:

  * `default` is required

* Python datatype `str`

### BOOLEAN

* Additional parameters in `INPUT_TYPES`:

  * `default` is required

* Python datatype `bool`

## Tensor datatypes

### IMAGE

* No additional parameters in `INPUT_TYPES`

* Python datatype `torch.Tensor` with *shape* \[B,H,W,C]

A batch of `B` images, height `H`, width `W`, with `C` channels (generally `C=3` for `RGB`).

### LATENT

* No additional parameters in `INPUT_TYPES`

* Python datatype `dict`, containing a `torch.Tensor` with *shape* \[B,C,H,W]

The `dict` passed contains the key `samples`, which is a `torch.Tensor` with *shape* \[B,C,H,W] representing
a batch of `B` latents, with `C` channels (generally `C=4` for existing stable diffusion models), height `H`, width `W`.

The height and width are 1/8 of the corresponding image size (which is the value you set in the Empty Latent Image node).

Other entries in the dictionary contain things like latent masks.

{/* TODO new SD models might have different C values? */}

### MASK

* No additional parameters in `INPUT_TYPES`

* Python datatype `torch.Tensor` with *shape* \[H,W] or \[B,C,H,W]

### AUDIO

* No additional parameters in `INPUT_TYPES`

* Python datatype `dict`, containing a `torch.Tensor` with *shape* \[B, C, T] and a sample rate.

The `dict` passed contains the key `waveform`, which is a `torch.Tensor` with *shape* \[B, C, T] representing a batch of `B` audio samples, with `C` channels (`C=2` for stereo and `C=1` for mono), and `T` time steps (i.e., the number of audio samples).

The `dict` contains another key `sample_rate`, which indicates the sampling rate of the audio.

## Custom Sampling datatypes

### Noise

The `NOISE` datatype represents a *source* of noise (not the actual noise itself). It can be represented by any Python object
that provides a method to generate noise, with the signature `generate_noise(self, input_latent:Tensor) -> Tensor`, and a
property, `seed:Optional[int]`.

<Tip>The `seed` is passed into `sample` guider in the `SamplerCustomAdvanced`, but does not appear to be used in any of the standard guiders.
It is Optional, so you can generally set it to None.</Tip>

When noise is to be added, the latent is passed into this method, which should return a `Tensor` of the same shape containing the noise.

See the [noise mixing example](./snippets#creating-noise-variations)

### Sampler

The `SAMPLER` datatype represents a sampler, which is represented as a Python object providing a `sample` method.
Stable diffusion sampling is beyond the scope of this guide; see `comfy/samplers.py` if you want to dig into this part of the code.

### Sigmas

The `SIGMAS` datatypes represents the values of sigma before and after each step in the sampling process, as produced by a scheduler.
This is represented as a one-dimensional tensor, of length `steps+1`, where each element represents the noise expected to be present
before the corresponding step, with the final value representing the noise present after the final step.

A `normal` scheduler, with 20 steps and denoise of 1, for an SDXL model, produces:

```
tensor([14.6146, 10.7468,  8.0815,  6.2049,  4.8557,  
         3.8654,  3.1238,  2.5572,  2.1157,  1.7648,  
         1.4806,  1.2458,  1.0481,  0.8784,  0.7297,  
         0.5964,  0.4736,  0.3555,  0.2322,  0.0292,  0.0000])
```

<Tip>The starting value of sigma depends on the model, which is why a scheduler node requires a `MODEL` input to produce a SIGMAS output</Tip>

### Guider

A `GUIDER` is a generalisation of the denoising process, as 'guided' by a prompt or any other form of conditioning. In Comfy the guider is
represented by a `callable` Python object providing a `__call__(*args, **kwargs)` method which is called by the sample.

The `__call__` method takes (in `args[0]`) a batch of noisy latents (tensor `[B,C,H,W]`), and returns a prediction of the noise (a tensor of the same shape).

## Model datatypes

There are a number of more technical datatypes for stable diffusion models. The most significant ones are `MODEL`, `CLIP`, `VAE` and `CONDITIONING`.
Working with these is (for the time being) beyond the scope of this guide! {/* TODO but maybe not forever */}

## Additional Parameters

Below is a list of officially supported keys that can be used in the 'extra options' portion of an input definition.

<Warning>You can use additional keys for your own custom widgets, but should *not* reuse any of the keys below for other purposes.</Warning>

| Key              | Description                                                                                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `default`        | The default value of the widget                                                                                                                                                                  |
| `min`            | The minimum value of a number (`FLOAT` or `INT`)                                                                                                                                                 |
| `max`            | The maximum value of a number (`FLOAT` or `INT`)                                                                                                                                                 |
| `step`           | The amount to increment or decrement a widget                                                                                                                                                    |
| `label_on`       | The label to use in the UI when the bool is `True` (`BOOL`)                                                                                                                                      |
| `label_off`      | The label to use in the UI when the bool is `False` (`BOOL`)                                                                                                                                     |
| `defaultInput`   | Defaults to an input socket rather than a supported widget                                                                                                                                       |
| `forceInput`     | `defaultInput` and also don't allow converting to a widget                                                                                                                                       |
| `multiline`      | Use a multiline text box (`STRING`)                                                                                                                                                              |
| `placeholder`    | Placeholder text to display in the UI when empty (`STRING`)                                                                                                                                      |
| `dynamicPrompts` | Causes the front-end to evaluate dynamic prompts                                                                                                                                                 |
| `lazy`           | Declares that this input uses [Lazy Evaluation](./lazy_evaluation)                                                                                                                               |
| `rawLink`        | When a link exists, rather than receiving the evaluated value, you will receive the link (i.e. `["nodeId", <outputIndex>]`). Primarily useful when your node uses [Node Expansion](./expansion). |









# Images, Latents, and Masks

When working with these datatypes, you will need to know about the `torch.Tensor` class.
Complete documentation is [here](https://pytorch.org/docs/stable/tensors.html), or
an introduction to the key concepts required for Comfy [here](./tensors).

<Warning>If your node has a single output which is a tensor, remember to return `(image,)` not `(image)`</Warning>

Most of the concepts below are illustrated in the [example code snippets](./snippets).

## Images

An IMAGE is a `torch.Tensor` with shape `[B,H,W,C]`, `C=3`. If you are going to save or load images, you will
need to convert to and from `PIL.Image` format - see the code snippets below! Note that some `pytorch` operations
offer (or expect) `[B,C,H,W]`, known as 'channel first', for reasons of computational efficiency. Just be careful.

### Working with PIL.Image

If you want to load and save images, you'll want to use PIL:

```python  theme={null}
from PIL import Image, ImageOps
```

## Masks

A MASK is a `torch.Tensor` with shape `[B,H,W]`.
In many contexts, masks have binary values (0 or 1), which are used to indicate which pixels should undergo specific operations.
In some cases values between 0 and 1 are used indicate an extent of masking, (for instance, to alter transparency, adjust filters, or composite layers).

### Masks from the Load Image Node

The `LoadImage` node uses an image's alpha channel (the "A" in "RGBA") to create MASKs.
The values from the alpha channel are normalized to the range \[0,1] (torch.float32) and then inverted.
The `LoadImage` node always produces a MASK output when loading an image. Many images (like JPEGs) don't have an alpha channel.
In these cases, `LoadImage` creates a default mask with the shape `[1, 64, 64]`.

### Understanding Mask Shapes

In libraries like `numpy`, `PIL`, and many others, single-channel images (like masks) are typically represented as 2D arrays, shape `[H,W]`.
This means the `C` (channel) dimension is implicit, and thus unlike IMAGE types, batches of MASKs have only three dimensions: `[B, H, W]`.
It is not uncommon to encounter a mask which has had the `B` dimension implicitly squeezed, giving a tensor `[H,W]`.

To use a MASK, you will often have to match shapes by unsqueezing to produce a shape `[B,H,W,C]` with `C=1`
To unsqueezing the `C` dimension, so you should `unsqueeze(-1)`, to unsqueeze `B`, you `unsqueeze(0)`.
If your node receives a MASK as input, you would be wise to always check `len(mask.shape)`.

## Latents

A LATENT is a `dict`; the latent sample is referenced by the key `samples` and has shape `[B,C,H,W]`, with `C=4`.

<Tip>LATENT is channel first, IMAGE is channel last</Tip>







# Hidden and Flexible inputs

## Hidden inputs

Alongside the `required` and `optional` inputs, which create corresponding inputs or widgets on the client-side,
there are three `hidden` input options which allow the custom node to request certain information from the server.

These are accessed by returning a value for `hidden` in the `INPUT_TYPES` `dict`, with the signature `dict[str,str]`,
containing one or more of `PROMPT`, `EXTRA_PNGINFO`, or `UNIQUE_ID`

```python  theme={null}
@classmethod
def INPUT_TYPES(s):
    return {
        "required": {...},
        "optional": {...},
        "hidden": {
            "unique_id": "UNIQUE_ID",
            "prompt": "PROMPT", 
            "extra_pnginfo": "EXTRA_PNGINFO",
        }
    }
```

### UNIQUE\_ID

`UNIQUE_ID` is the unique identifier of the node, and matches the `id` property of the node on the client side.
It is commonly used in client-server communications (see [messages](/development/comfyui-server/comms_messages#getting-node-id)).

### PROMPT

`PROMPT` is the complete prompt sent by the client to the server.
See [the prompt object](/custom-nodes/js/javascript_objects_and_hijacking#prompt) for a full description.

### EXTRA\_PNGINFO

`EXTRA_PNGINFO` is a dictionary that will be copied into the metadata of any `.png` files saved. Custom nodes can store additional
information in this dictionary for saving (or as a way to communicate with a downstream node).

<Tip>Note that if Comfy is started with the `disable_metadata` option, this data won't be saved.</Tip>

### DYNPROMPT

`DYNPROMPT` is an instance of `comfy_execution.graph.DynamicPrompt`. It differs from `PROMPT` in that it may mutate during the course of execution in response to [Node Expansion](/custom-nodes/backend/expansion).
<Tip>`DYNPROMPT` should only be used for advanced cases (like implementing loops in custom nodes).</Tip>

## Flexible inputs

### Custom datatypes

If you want to pass data between your own custom nodes, you may find it helpful to define a custom datatype. This is (almost) as simple as
just choosing a name for the datatype, which should be a unique string in upper case, such as `CHEESE`.

You can then use `CHEESE` in your node `INPUT_TYPES` and `RETURN_TYPES`, and the Comfy client will only allow `CHEESE` outputs to connect to a `CHEESE` input.
`CHEESE` can be any python object.

The only point to note is that because the Comfy client doesn't know about `CHEESE` you need (unless you define a custom widget for `CHEESE`,
which is a topic for another day), to force it to be an input rather than a widget. This can be done with the `forceInput` option in the input options dictionary:

```python  theme={null}
@classmethod
def INPUT_TYPES(s):
    return {
        "required": { "my_cheese": ("CHEESE", {"forceInput":True}) }
    }
```

### Wildcard inputs

```python  theme={null}
@classmethod
def INPUT_TYPES(s):
    return {
        "required": { "anything": ("*",{})},
    }

@classmethod
def VALIDATE_INPUTS(s, input_types):
    return True
```

The frontend allows `*` to indicate that an input can be connected to any source. Because this is not officially supported by the backend, you can skip the backend validation of types by accepting a parameter named `input_types` in your `VALIDATE_INPUTS` function. (See [VALIDATE\_INPUTS](./server_overview#validate-inputs) for more information.)
It's up to the node to make sense of the data that is passed.

### Dynamically created inputs

If inputs are dynamically created on the client side, they can't be defined in the Python source code.
In order to access this data we need an `optional` dictionary that allows Comfy to pass data with
arbitrary names. Since the Comfy server

```python  theme={null}
class ContainsAnyDict(dict):
    def __contains__(self, key):
        return True
...

@classmethod
def INPUT_TYPES(s):
    return {
        "required": {},
        "optional": ContainsAnyDict()
    }
...

def main_method(self, **kwargs):
    # the dynamically created input data will be in the dictionary kwargs

```

<Tip>Hat tip to rgthree for this pythonic trick!</Tip>












# Lazy Evaluation

## Lazy Evaluation

By default, all `required` and `optional` inputs are evaluated before a node can be run. Sometimes, however, an
input won't necessarily be used and evaluating it would result in unnecessary processing. Here are some examples
of nodes where lazy evaluation may be beneficial:

1. A `ModelMergeSimple` node where the ratio is either `0.0` (in which case the first model doesn't need to be loaded)
   or `1.0` (in which case the second model doesn't need to be loaded).
2. Interpolation between two images where the ratio (or mask) is either entirely `0.0` or entirely `1.0`.
3. A Switch node where one input determines which of the other inputs will be passed through.

<Tip>There is very little cost in making an input lazy. If it's something you can do, you generally should.</Tip>

### Creating Lazy Inputs

There are two steps to making an input a "lazy" input. They are:

1. Mark the input as lazy in the dictionary returned by `INPUT_TYPES`
2. Define a method named `check_lazy_status` (note: *not* a class method) that will be called prior to evaluation to determine if any more inputs are necessary.

To demonstrate these, we'll make a "MixImages" node that interpolates between two images according to a mask. If the entire mask is `0.0`, we don't need to evaluate any part of the tree leading up to the second image. If the entire mask is `1.0`, we can skip evaluating the first image.

#### Defining `INPUT_TYPES`

Declaring that an input is lazy is as simple as adding a `lazy: True` key-value pair to the input's options dictionary.

```python  theme={null}
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "image1": ("IMAGE",{"lazy": True}),
            "image2": ("IMAGE",{"lazy": True}),
            "mask": ("MASK",),
        },
    }
```

In this example, `image1` and `image2` are both marked as lazy inputs, but `mask` will always be evaluated.

#### Defining `check_lazy_status`

A `check_lazy_status` method is called if there are one or more lazy inputs that are not yet available. This method receives the same arguments as the standard execution function. All available inputs are passed in with their final values while unavailable lazy inputs have a value of `None`.

The responsibility of the `check_lazy_status` function is to return a list of the names of any lazy inputs that are needed to proceed. If all lazy inputs are available, the function should return an empty list.

Note that `check_lazy_status` may be called multiple times. (For example, you might find after evaluating one lazy input that you need to evaluate another.)

<Tip>Note that because the function uses actual input values, it is *not* a class method.</Tip>

```python  theme={null}
def check_lazy_status(self, mask, image1, image2):
    mask_min = mask.min()
    mask_max = mask.max()
    needed = []
    if image1 is None and (mask_min != 1.0 or mask_max != 1.0):
        needed.append("image1")
    if image2 is None and (mask_min != 0.0 or mask_max != 0.0):
        needed.append("image2")
    return needed
```

### Full Example

```python  theme={null}
class LazyMixImages:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",{"lazy": True}),
                "image2": ("IMAGE",{"lazy": True}),
                "mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "mix"

    CATEGORY = "Examples"

    def check_lazy_status(self, mask, image1, image2):
        mask_min = mask.min()
        mask_max = mask.max()
        needed = []
        if image1 is None and (mask_min != 1.0 or mask_max != 1.0):
            needed.append("image1")
        if image2 is None and (mask_min != 0.0 or mask_max != 0.0):
            needed.append("image2")
        return needed

    # Not trying to handle different batch sizes here just to keep the demo simple
    def mix(self, mask, image1, image2):
        mask_min = mask.min()
        mask_max = mask.max()
        if mask_min == 0.0 and mask_max == 0.0:
            return (image1,)
        elif mask_min == 1.0 and mask_max == 1.0:
            return (image2,)

        result = image1 * (1. - mask) + image2 * mask,
        return (result[0],)
```

## Execution Blocking

While Lazy Evaluation is the recommended way to "disable" part of a graph, there are times when you want to disable an `OUTPUT` node that doesn't implement lazy evaluation itself. If it's an output node that you developed yourself, you should just add lazy evaluation as follows:

1. Add a required (if this is a new node) or optional (if you care about backward compatibility) input for `enabled` that defaults to `True`
2. Make all other inputs `lazy` inputs
3. Only evaluate the other inputs if `enabled` is `True`

If it's not a node you control, you can make use of a `comfy_execution.graph.ExecutionBlocker`. This special object can be returned as an output from any socket. Any nodes which receive an `ExecutionBlocker` as input will skip execution and return that `ExecutionBlocker` for any outputs.

<Tip>**There is intentionally no way to stop an ExecutionBlocker from propagating forward.** If you think you want this, you should really be using Lazy Evaluation.</Tip>

### Usage

There are two ways to construct and use an `ExecutionBlocker`

1. Pass `None` into the constructor to silently block execution. This is useful for cases where blocking execution is part of a successful run -- like disabling an output.

```python  theme={null}
def silent_passthrough(self, passthrough, blocked):
    if blocked:
        return (ExecutionBlocker(None),)
    else:
        return (passthrough,)
```

2. Pass a string into the constructor to display an error message when a node is blocked due to receiving the object. This can be useful if you want to display a meaningful error message if someone uses a meaningless output -- for example, the `VAE` output when loading a model that doesn't contain VAEs.

```python  theme={null}
def load_checkpoint(self, ckpt_name):
    ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
    model, clip, vae = load_checkpoint(ckpt_path)
    if vae is None:
        # This error is more useful than a "'NoneType' has no attribute" error
        # in a later node
        vae = ExecutionBlocker(f"No VAE contained in the loaded model {ckpt_name}")
    return (model, clip, vae)
```









# Node Expansion

## Node Expansion

Normally, when a node is executed, that execution function immediately returns the output results of that node. "Node Expansion" is a relatively advanced technique that allows nodes to return a new subgraph of nodes that should take its place in the graph. This technique is what allows custom nodes to implement loops.

### A Simple Example

First, here's a simple example of what node expansion looks like:

<Tip>We highly recommend using the `GraphBuilder` class when creating subgraphs. It isn't mandatory, but it prevents you from making many easy mistakes.</Tip>

```python  theme={null}
def load_and_merge_checkpoints(self, checkpoint_path1, checkpoint_path2, ratio):
    from comfy_execution.graph_utils import GraphBuilder # Usually at the top of the file
    graph = GraphBuilder()
    checkpoint_node1 = graph.node("CheckpointLoaderSimple", checkpoint_path=checkpoint_path1)
    checkpoint_node2 = graph.node("CheckpointLoaderSimple", checkpoint_path=checkpoint_path2)
    merge_model_node = graph.node("ModelMergeSimple", model1=checkpoint_node1.out(0), model2=checkpoint_node2.out(0), ratio=ratio)
    merge_clip_node = graph.node("ClipMergeSimple", clip1=checkpoint_node1.out(1), clip2=checkpoint_node2.out(1), ratio=ratio)
    return {
        # Returning (MODEL, CLIP, VAE) outputs
        "result": (merge_model_node.out(0), merge_clip_node.out(0), checkpoint_node1.out(2)),
        "expand": graph.finalize(),
    }
```

While this same node could previously be implemented by manually calling into ComfyUI internals, using expansion means that each subnode will be cached separately (so if you change `model2`, you don't have to reload `model1`).

### Requirements

In order to perform node expansion, a node must return a dictionary with the following keys:

1. `result`: A tuple of the outputs of the node. This may be a mix of finalized values (like you would return from a normal node) and node outputs.
2. `expand`: The finalized graph to perform expansion on. See below if you are not using the `GraphBuilder`.

#### Additional Requirements if not using GraphBuilder

The format expected from the `expand` key is the same as the ComfyUI API format. The following requirements are handled by the `GraphBuilder`, but must be handled manually if you choose to forego it:

1. Node IDs must be unique across the entire graph. (This includes between multiple executions of the same node due to the use of lists.)
2. Node IDs must be deterministic and consistent between multiple executions of the graph (including partial executions due to caching).

Even if you don't want to use the `GraphBuilder` for actually building the graph (e.g. because you're loading the raw json of the graph from a file), you can use the `GraphBuilder.alloc_prefix()` function to generate a prefix and `comfy.graph_utils.add_graph_prefix` to fix existing graphs to meet these requirements.

### Efficient Subgraph Caching

While you can pass non-literal inputs to nodes within the subgraph (like torch tensors), this can inhibit caching *within* the subgraph. When possible, you should pass links to subgraph objects rather than the node itself. (You can declare an input as a `rawLink` within the input's [Additional Parameters](./datatypes#additional-parameters) to do this easily.)

## See Also

* [Subgraphs (Developer Guide)](/custom-nodes/js/subgraphs) — Frontend guide for extension authors






# Data lists

## Length one processing

Internally, the Comfy server represents data flowing from one node to the next as a Python `list`, normally length 1, of the relevant datatype.
In normal operation, when a node returns an output, each element in the output `tuple` is separately wrapped in a list (length 1); then when the
next node is called, the data is unwrapped and passed to the main function.

<Tip>You generally don't need to worry about this, since Comfy does the wrapping and unwrapping.</Tip>

<Tip>This isn't about batches. A batch (of, for instance, latents, or images) is a *single entry* in the list (see [tensor datatypes](./images_and_masks))</Tip>

## List processing

In some circumstance, multiple data instances are processed in a single workflow, in which case the internal data will be a list containing the data instances.
An example of this might be processing a series of images one at a time to avoid running out of VRAM, or handling images of different sizes.

By default, Comfy will process the values in the list sequentially:

* if the inputs are `list`s of different lengths, the shorter ones are padded by repeating the last value
* the main method is called once for each value in the input lists
* the outputs are `list`s, each of which is the same length as the longest input

The relevant code can be found in the method `map_node_over_list` in `execution.py`.

However, as Comfy wraps node outputs into a `list` of length one, if the `tuple` returned by
a custom node contains a `list`, that `list` will be wrapped, and treated as a single piece of data.
In order to tell Comfy that the list being returned should not be wrapped, but treated as a series of data for sequential processing,
the node should provide a class attribute `OUTPUT_IS_LIST`, which is a `tuple[bool]`, of the same length as `RETURN_TYPES`, specifying
which outputs which should be so treated.

A node can also override the default input behaviour and receive the whole list in a single call. This is done by setting a class attribute
`INPUT_IS_LIST` to `True`.

Here's a (lightly annotated) example from the built in nodes - `ImageRebatch` takes one or more batches of images (received as a list, because `INPUT_IS_LIST - True`)
and rebatches them into batches of the requested size.

<Tip>`INPUT_IS_LIST` is node level - all inputs get the same treatment. So the value of the `batch_size` widget is given by `batch_size[0]`.</Tip>

```Python  theme={null}

class ImageRebatch:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "images": ("IMAGE",),
                              "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}) }}
    RETURN_TYPES = ("IMAGE",)
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True, )
    FUNCTION = "rebatch"
    CATEGORY = "image/batch"

    def rebatch(self, images, batch_size):
        batch_size = batch_size[0]    # everything comes as a list, so batch_size is list[int]

        output_list = []
        all_images = []
        for img in images:                    # each img is a batch of images
            for i in range(img.shape[0]):     # each i is a single image
                all_images.append(img[i:i+1])

        for i in range(0, len(all_images), batch_size): # take batch_size chunks and turn each into a new batch
            output_list.append(torch.cat(all_images[i:i+batch_size], dim=0))  # will die horribly if the image batches had different width or height!

        return (output_list,)
```

#### INPUT\_IS\_LIST




# Annotated Examples

A growing collection of fragments of example code...

## Images and Masks

### Load an image

Load an image into a batch of size 1 (based on `LoadImage` source code in `nodes.py`)

```python  theme={null}
i = Image.open(image_path)
i = ImageOps.exif_transpose(i)
if i.mode == 'I':
    i = i.point(lambda i: i * (1 / 255))
image = i.convert("RGB")
image = np.array(image).astype(np.float32) / 255.0
image = torch.from_numpy(image)[None,]
```

### Save an image batch

Save a batch of images (based on `SaveImage` source code in `nodes.py`)

```python  theme={null}
for (batch_number, image) in enumerate(images):
    i = 255. * image.cpu().numpy()
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    filepath = # some path that takes the batch number into account
    img.save(filepath)
```

### Invert a mask

Inverting a mask is a straightforward process. Since masks are normalised to the range \[0,1]:

```python  theme={null}
mask = 1.0 - mask
```

### Convert a mask to Image shape

```Python  theme={null}
# We want [B,H,W,C] with C = 1
if len(mask.shape)==2: # we have [H,W], so insert B and C as dimension 1
    mask = mask[None,:,:,None]
elif len(mask.shape)==3 and mask.shape[2]==1: # we have [H,W,C]
    mask = mask[None,:,:,:]
elif len(mask.shape)==3:                      # we have [B,H,W]
    mask = mask[:,:,:,None]
```

### Using Masks as Transparency Layers

When used for tasks like inpainting or segmentation, the MASK's values will eventually be rounded to the nearest integer so that they are binary — 0 indicating regions to be ignored and 1 indicating regions to be targeted. However, this doesn't happen until the MASK is passed to those nodes. This flexibility allows you to use MASKs as you would in digital photography contexts as a transparency layer:

```python  theme={null}
# Invert mask back to original transparency layer
mask = 1.0 - mask

# Unsqueeze the `C` (channels) dimension
mask = mask.unsqueeze(-1)

# Concatenate ("cat") along the `C` dimension
rgba_image = torch.cat((rgb_image, mask), dim=-1)
```

## Noise

### Creating noise variations

Here's an example of creating a noise object which mixes the noise from two sources. This could be used to create slight noise variations by varying `weight2`.

```python  theme={null}
class Noise_MixedNoise:
    def __init__(self, nosie1, noise2, weight2):
        self.noise1  = noise1
        self.noise2  = noise2
        self.weight2 = weight2

    @property
    def seed(self): return self.noise1.seed

    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        noise1 = self.noise1.generate_noise(input_latent)
        noise2 = self.noise2.generate_noise(input_latent)
        return noise1 * (1.0-self.weight2) + noise2 * (self.weight2)
```




# Working with torch.Tensor

## pytorch, tensors, and torch.Tensor

All the core number crunching in Comfy is done by [pytorch](https://pytorch.org/). If your custom nodes are going
to get into the guts of stable diffusion you will need to become familiar with this library, which is way beyond
the scope of this introduction.

However, many custom nodes will need to manipulate images, latents and masks, each of which are represented internally
as `torch.Tensor`, so you'll want to bookmark the
[documentation for torch.Tensor](https://pytorch.org/docs/stable/tensors.html).

### What is a Tensor?

`torch.Tensor` represents a tensor, which is the mathematical generalization of a vector or matrix to any number of dimensions.
A tensor's *rank* is the number of dimensions it has (so a vector has *rank* 1, a matrix *rank* 2); its *shape* describes the
size of each dimension.

So an RGB image (of height H and width W) might be thought of as three arrays (one for each color channel), each measuring H x W,
which could be represented as a tensor with *shape* `[H,W,3]`. In Comfy images almost always come in a batch (even if the batch
only contains a single image). `torch` always places the batch dimension first, so Comfy images have *shape* `[B,H,W,3]`, generally
written as `[B,H,W,C]` where C stands for Channels.

### squeeze, unsqueeze, and reshape

If a tensor has a dimension of size 1 (known as a collapsed dimension), it is equivalent to the same tensor with that dimension removed
(a batch with 1 image is just an image). Removing such a collapsed dimension is referred to as squeezing, and
inserting one is known as unsqueezing.

<Warning>Some torch code, and some custom node authors, will return a squeezed tensor when a dimension is collapsed - such
as when a batch has only one member. This is a common cause of bugs!</Warning>

To represent the same data in a different shape is referred to as reshaping. This often requires you to know
the underlying data structure, so handle with care!

### Important notation

`torch.Tensor` supports most Python slice notation, iteration, and other common list-like operations. A tensor
also has a `.shape` attribute which returns its size as a `torch.Size` (which is a subclass of `tuple` and can
be treated as such).

There are some other important bits of notation you'll often see (several of these are less common
standard Python notation, seen much more frequently when dealing with tensors)

* `torch.Tensor` supports the use of `None` in slice notation
  to indicate the insertion of a dimension of size 1.

* `:` is frequently used when slicing a tensor; this simply means 'keep the whole dimension'.
  It's like using `a[start:end]` in Python, but omitting the start point and end point.

* `...` represents 'the whole of an unspecified number of dimensions'. So `a[0, ...]` would extract the first
  item from a batch regardless of the number of dimensions.

* in methods which require a shape to be passed, it is often passed as a `tuple` of the dimensions, in
  which a single dimension can be given the size `-1`, indicating that the size of this dimension should
  be calculated based on the total size of the data.

```python  theme={null}
>>> a = torch.Tensor((1,2))
>>> a.shape
torch.Size([2])
>>> a[:,None].shape 
torch.Size([2, 1])
>>> a.reshape((1,-1)).shape
torch.Size([1, 2])
```

### Elementwise operations

Many binary on `torch.Tensor` (including '+', '-', '\*', '/' and '==') are applied elementwise (independently applied to each element).
The operands must be *either* two tensors of the same shape, *or* a tensor and a scalar. So:

```python  theme={null}
>>> import torch
>>> a = torch.Tensor((1,2))
>>> b = torch.Tensor((3,2))
>>> a*b
tensor([3., 4.])
>>> a/b
tensor([0.3333, 1.0000])
>>> a==b
tensor([False,  True])
>>> a==1
tensor([ True, False])
>>> c = torch.Tensor((3,2,1)) 
>>> a==c
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: The size of tensor a (2) must match the size of tensor b (3) at non-singleton dimension 0
```

### Tensor truthiness

<Warning>The 'truthiness' value of a Tensor is not the same as that of Python lists.</Warning>

You may be familiar with the truthy value of a Python list as `True` for any non-empty list, and `False` for `None` or `[]`.
By contrast A `torch.Tensor` (with more than one elements) does not have a defined truthy value. Instead you need to use
`.all()` or `.any()` to combine the elementwise truthiness:

```python  theme={null}
>>> a = torch.Tensor((1,2))
>>> print("yes" if a else "no")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: Boolean value of Tensor with more than one value is ambiguous
>>> a.all()
tensor(False)
>>> a.any()
tensor(True)
```

This also means that you need to use `if a is not None:` not `if a:` to determine if a tensor variable has been set.






# Node replacement

> Register node replacements to help users migrate from deprecated nodes

The Node Replacement API allows custom node developers to define migration paths from deprecated nodes to their newer equivalents. When you update or rename nodes, users can automatically upgrade their workflows.

## When to use

* **Changing node class names**: You changed a node's class name (use `DISPLAY_NAME` for display name changes instead)
* **Merging nodes**: Multiple nodes consolidated into one (e.g., `Load3DAnimation` merged into `Load3D`)
* **Refactoring inputs**: Input names or types changed between versions
* **Fixing typos**: Correcting node names without breaking existing workflows

## Where to register replacements

Register replacements during your extension's `on_load` lifecycle hook. Create a dedicated file (e.g., `node_replacements.py`) in your custom node package:

```
my_custom_nodes/
├── __init__.py
├── nodes.py
└── node_replacements.py   # Register replacements here
```

## Complete example

Here's a full example showing how to structure node replacements in a custom node package:

```python  theme={null}
# node_replacements.py
from comfy_api.latest import ComfyExtension, io, ComfyAPI

api = ComfyAPI()


async def register_my_replacements():
    """Register all node replacements for this package."""
    
    # Simple rename - no input changes needed
    await api.node_replacement.register(io.NodeReplace(
        new_node_id="MyNewNode",
        old_node_id="MyOldNode",
    ))
    
    # Complex replacement with input mapping
    await api.node_replacement.register(io.NodeReplace(
        new_node_id="MyImprovedSampler",
        old_node_id="MyOldSampler",
        old_widget_ids=["steps", "cfg"],
        input_mapping=[
            {"new_id": "model", "old_id": "model"},
            {"new_id": "num_steps", "old_id": "steps"},
            {"new_id": "guidance", "old_id": "cfg"},
            {"new_id": "scheduler", "set_value": "normal"},  # New input with default
        ],
        output_mapping=[
            {"new_idx": 0, "old_idx": 0},
        ],
    ))


class MyExtension(ComfyExtension):
    async def on_load(self) -> None:
        await register_my_replacements()

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return []  # No nodes defined here, just replacements


async def comfy_entrypoint() -> MyExtension:
    return MyExtension()
```

## Core examples

ComfyUI core uses node replacements for built-in node migrations. Here are real examples from [`comfy_extras/nodes_replacements.py`](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_replacements.py):

### Simple node merge

When `Load3DAnimation` was merged into `Load3D`:

```python  theme={null}
await api.node_replacement.register(io.NodeReplace(
    new_node_id="Load3D",
    old_node_id="Load3DAnimation",
))
```

### Typo fix

Correcting a typo in `SDV_img2vid_Conditioning` → `SVD_img2vid_Conditioning`:

```python  theme={null}
await api.node_replacement.register(io.NodeReplace(
    new_node_id="SVD_img2vid_Conditioning",
    old_node_id="SDV_img2vid_Conditioning",
))
```

### Input renaming with defaults

Replacing `ImageScaleBy` with `ResizeImageMaskNode`:

```python  theme={null}
await api.node_replacement.register(io.NodeReplace(
    new_node_id="ResizeImageMaskNode",
    old_node_id="ImageScaleBy",
    old_widget_ids=["upscale_method", "scale_by"],
    input_mapping=[
        {"new_id": "input", "old_id": "image"},
        {"new_id": "resize_type", "set_value": "scale by multiplier"},
        {"new_id": "resize_type.multiplier", "old_id": "scale_by"},
        {"new_id": "scale_method", "old_id": "upscale_method"},
    ],
))
```

### Autogrow input mapping

For nodes using Autogrow (dynamic inputs), use dot notation:

```python  theme={null}
await api.node_replacement.register(io.NodeReplace(
    new_node_id="BatchImagesNode",
    old_node_id="ImageBatch",
    input_mapping=[
        {"new_id": "images.image0", "old_id": "image1"},
        {"new_id": "images.image1", "old_id": "image2"},
    ],
))
```

## NodeReplace parameters

| Parameter        | Type               | Description                                               |
| ---------------- | ------------------ | --------------------------------------------------------- |
| `new_node_id`    | str                | Class name of the replacement node                        |
| `old_node_id`    | str                | Class name of the deprecated node                         |
| `old_widget_ids` | list\[str] \| None | Ordered list binding widget IDs to their relative indexes |
| `input_mapping`  | list \| None       | How to map inputs from old to new node                    |
| `output_mapping` | list \| None       | How to map outputs from old to new node                   |

## Input mapping

Each input mapping entry defines how an input transfers from the old node to the new one.

**Map from old input:**

```python  theme={null}
{"new_id": "model", "old_id": "model"}
```

**Set a fixed value:**

```python  theme={null}
{"new_id": "scheduler", "set_value": "normal"}
```

**Map dynamic/autogrow inputs (use dot notation):**

```python  theme={null}
{"new_id": "images.image0", "old_id": "image1"}
```

## Output mapping

Output mappings use index-based references:

```python  theme={null}
{"new_idx": 0, "old_idx": 0}  # Map first output
{"new_idx": 1, "old_idx": 0}  # Old output 0 -> new output 1
```

## Widget ID binding

The `old_widget_ids` field maps widget IDs to their positional indexes. This is required because workflow JSON stores widget values by position, not ID.

```python  theme={null}
old_widget_ids=["steps", "cfg", "sampler"]
# Widget at index 0 = "steps"
# Widget at index 1 = "cfg"
# Widget at index 2 = "sampler"
```

## REST API

Retrieve all registered replacements:

```
GET /api/node_replacements
```

**Response:**

```json  theme={null}
{
  "OldSamplerNode": [
    {
      "new_node_id": "NewSamplerNode",
      "old_node_id": "OldSamplerNode",
      "old_widget_ids": ["num_steps", "cfg_scale", "sampler_name"],
      "input_mapping": [
        {"new_id": "model", "old_id": "model"},
        {"new_id": "steps", "old_id": "num_steps"},
        {"new_id": "scheduler", "set_value": "normal"}
      ],
      "output_mapping": [
        {"new_idx": 0, "old_idx": 0}
      ]
    }
  ]
}
```

## Frontend behavior

When a workflow contains a deprecated node, the frontend:

1. Fetches replacements from `GET /api/node_replacements`
2. Detects nodes matching `old_node_id`
3. Prompts the user to upgrade
4. Applies input/output mappings automatically
5. Preserves connections and widget values

See the frontend implementation:

* [Business logic PR #8364](https://github.com/Comfy-Org/ComfyUI_frontend/pull/8364)
* [Additional logic PR #8483](https://github.com/Comfy-Org/ComfyUI_frontend/pull/8483)
* [UI views PR #8604](https://github.com/Comfy-Org/ComfyUI_frontend/pull/8604)






# Javascript Extensions

## Extending the Comfy Client

Comfy can be modified through an extensions mechanism. To add an extension you need to:

* Export `WEB_DIRECTORY` from your Python module,
* Place one or more `.js` files into that directory,
* Use `app.registerExtension` to register your extension.

These three steps are below. Once you know how to add an extension, look
through the [hooks](/custom-nodes/js/javascript_hooks) available to get your code called,
a description of various [Comfy objects](/custom-nodes/js/javascript_objects_and_hijacking) you might need,
or jump straight to some [example code snippets](/custom-nodes/js/javascript_examples).

### Exporting `WEB_DIRECTORY`

The Comfy web client can be extended by creating a subdirectory in your custom node directory, conventionally called `js`, and
exporting `WEB_DIRECTORY` - so your `__init_.py` will include something like:

```python  theme={null}
WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
```

### Including `.js` files

<Tip>All Javascript `.js` files will be loaded by the browser as the Comfy webpage loads. You don't need to specify the file
your extension is in.</Tip>

*Only* `.js` files will be added to the webpage. Other resources (such as `.css` files) can be accessed
at `extensions/custom_node_subfolder/the_file.css` and added programmatically.

<Warning>That path does *not* include the name of the subfolder. The value of `WEB_DIRECTORY` is inserted by the server.</Warning>

### Registering an extension

The basic structure of an extension follows is to import the main Comfy `app` object, and call `app.registerExtension`,
passing a dictionary that contains a unique `name`,
and one or more functions to be called by hooks in the Comfy code.

A complete, trivial, and annoying, extension might look like this:

```Javascript  theme={null}
import { app } from "../../scripts/app.js";
app.registerExtension({ 
	name: "a.unique.name.for.a.useless.extension",
	async setup() { 
		alert("Setup complete!")
	},
})
```




# Comfy Hooks

## Extension hooks

At various points during Comfy execution, the application calls
`#invokeExtensionsAsync` or `#invokeExtensions` with the name of a hook.
These invoke, on all registered extensions, the appropriately named method (if present), such as `setup`
in the example above.

Comfy provides a variety of hooks for custom extension code to use to modify client behavior.

<Tip>These hooks are called during creation and modification of the Comfy client side elements.
<br />Events during workflow execution are handled by
the `apiUpdateHandlers`</Tip> {/* TODO link when written */}

A few of the most significant hooks are described below.
As Comfy is being actively developed, from time to time additional hooks are added, so
search for `#invokeExtensions` in `app.js` to find all available hooks.

See also the [sequence](#call-sequences) in which hooks are invoked.

### Commonly used hooks

Start with `beforeRegisterNodeDef`, which is used by the majority of extensions, and is often the only one needed.

#### beforeRegisterNodeDef()

Called once for each node type (the list of nodes available in the `AddNode` menu), and is used to
modify the behaviour of the node.

```Javascript  theme={null}
async beforeRegisterNodeDef(nodeType, nodeData, app) 
```

The object passed in the `nodeType` parameter essentially serves as a template
for all nodes that will be created of this type, so modifications made to `nodeType.prototype` will apply
to all nodes of this type. `nodeData` is an encapsulation of aspects of the node defined in the Python code,
such as its category, inputs, and outputs. `app` is a reference to the main Comfy app object (which you
have already imported anyway!)

<Tip>This method is called, on each registered extension, for *every* node type, not just the ones added by that extension.</Tip>

The usual idiom is to check `nodeType.ComfyClass`, which holds the Python class name corresponding to this node,
to see if you need to modify the node. Often this means modifying the custom nodes that you have added,
although you may sometimes need to modify the behavior of other nodes (or other custom nodes
might modify yours!), in which case care should be taken to ensure interoperability.

<Tip>Since other extensions may also modify nodes, aim to write code that makes as few assumptions as possible.
And play nicely - isolate your changes wherever possible.</Tip>

A very common idiom in `beforeRegisterNodeDef` is to 'hijack' an existing method:

<Note>
  **Deprecated:** The prototype hijacking pattern shown below is deprecated and subject to change at any point in the near future. For context menus, use the official [Context Menu API](/custom-nodes/js/context-menu-migration) instead. For other use cases, prefer using the official [extension hooks](/custom-nodes/js/javascript_hooks) where available.
</Note>

```Javascript  theme={null}
async beforeRegisterNodeDef(nodeType, nodeData, app) {
	if (nodeType.comfyClass=="MyNodeClass") { 
		const onConnectionsChange = nodeType.prototype.onConnectionsChange;
		nodeType.prototype.onConnectionsChange = function (side,slot,connect,link_info,output) {     
			const r = onConnectionsChange?.apply(this, arguments);   
			console.log("Someone changed my connection!");
			return r;
		}
	}
}
```

In this idiom the existing prototype method is stored, and then replaced. The replacement calls the
original method (the `?.apply` ensures that if there wasn't one this is still safe) and then
performs additional operations. Depending on your code logic, you may need to place the `apply` elsewhere in your replacement code,
or even make calling it conditional.

When hijacking a method in this way, you will want to look at the core comfy code (breakpoints are your friend) to check
and conform with the method signature.

<Warning>This approach is fragile and may break with future ComfyUI updates. Use official APIs whenever possible.</Warning>

#### nodeCreated()

```Javascript  theme={null}
async nodeCreated(node)
```

Called when a specific instance of a node gets created
(right at the end of the `ComfyNode()` function on `nodeType` which serves as a constructor).
In this hook you can make modifications to individual instances of your node.

<Tip>Changes that apply to all instances are better added to the prototype in `beforeRegisterNodeDef` as described above.</Tip>

#### init()

```Javascript  theme={null}
async init()
```

Called when the Comfy webpage is loaded (or reloaded). The call is made after the graph object has been created, but before any
nodes are registered or created. It can be used to modify core Comfy behavior by hijacking methods of the app, or of the
graph (a `LiteGraph` object). This is discussed further in [Comfy Objects](./javascript_objects_and_hijacking).

<Warning>With great power comes great responsibility. Hijacking core behavior makes it more likely your nodes
will be incompatible with other custom nodes, or future Comfy updates</Warning>

#### setup()

```Javascript  theme={null}
async setup()
```

Called at the end of the startup process. A good place to add event listeners (either for Comfy events, or DOM events),
or adding to the global menus, both of which are discussed elsewhere. {/* TODO link when written */}

<Tip>To do something when a workflow has loaded, use `afterConfigureGraph`, not `setup`</Tip>

### Call sequences

These sequences were obtained by insert logging code into the Comfy `app.js` file. You may find similar code helpful
in understanding the execution flow.

```Javascript  theme={null}
/* approx line 220 at time of writing: */
	#invokeExtensions(method, ...args) {
		console.log(`invokeExtensions      ${method}`) // this line added
		// ...
	}
/* approx line 250 at time of writing: */
	async #invokeExtensionsAsync(method, ...args) {
		console.log(`invokeExtensionsAsync ${method}`) // this line added
		// ...
	}
```

#### Web page load

```
invokeExtensionsAsync init
invokeExtensionsAsync addCustomNodeDefs
invokeExtensionsAsync getCustomWidgets
invokeExtensionsAsync beforeRegisterNodeDef    [repeated multiple times]
invokeExtensionsAsync registerCustomNodes
invokeExtensionsAsync beforeConfigureGraph
invokeExtensionsAsync nodeCreated
invokeExtensions      loadedGraphNode
invokeExtensionsAsync afterConfigureGraph
invokeExtensionsAsync setup
```

#### Loading workflow

```
invokeExtensionsAsync beforeConfigureGraph
invokeExtensionsAsync beforeRegisterNodeDef   [zero, one, or multiple times]
invokeExtensionsAsync nodeCreated             [repeated multiple times]
invokeExtensions      loadedGraphNode         [repeated multiple times]
invokeExtensionsAsync afterConfigureGraph
```

#### Adding new node

```
invokeExtensionsAsync nodeCreated
```




# Comfy Objects

## LiteGraph

The Comfy UI is built on top of [LiteGraph](https://github.com/jagenjo/litegraph.js).
Much of the Comfy functionality is provided by LiteGraph, so if developing more complex
nodes you will probably find it helpful to clone that repository and browse the documentation,
which can be found at `doc/index.html`.

## ComfyApp

The `app` object (always accessible by `import { app } from "../../scripts/app.js";`) represents the Comfy application running in the browser,
and contains a number of useful properties and functions, some of which are listed below.

<Note>
  **Deprecated:** Hijacking/monkey-patching functions on `app` or prototypes is deprecated and subject to change at any point in the near future. Use the official [extension hooks](/custom-nodes/js/javascript_hooks) and [Context Menu API](/custom-nodes/js/context-menu-migration) instead.
</Note>

<Warning>Hijacking functions on `app` is not recommended, as Comfy is under constant development, and core behavior may change.</Warning>

### Properties

Important properties of `app` include (this is not an exhaustive list):

| property        | contents                                                                                                                                                        |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `canvas`        | An LGraphCanvas object, representing the current user interface. It contains some potentially interesting properties, such as `node_over` and `selected_nodes`. |
| `canvasEl`      | The DOM `<canvas>` element                                                                                                                                      |
| `graph`         | A reference to the LGraph object describing the current graph                                                                                                   |
| `runningNodeId` | During execution, the node currently being executed                                                                                                             |
| `ui`            | Provides access to some UI elements, such as the queue, menu, and dialogs                                                                                       |

`canvas` (for graphical elements) and `graph` (for logical connections) are probably the ones you are most likely to want to access.

### Functions

Again, there are many. A few significant ones are:

| function          | notes                                                                 |
| ----------------- | --------------------------------------------------------------------- |
| graphToPrompt     | Convert the graph into a prompt that can be sent to the Python server |
| loadGraphData     | Load a graph                                                          |
| queuePrompt       | Submit a prompt to the queue                                          |
| registerExtension | You've seen this one - used to add an extension                       |

## LGraph

The `LGraph` object is part of the LiteGraph framework, and represents the current logical state of the graph (nodes and links).
If you want to manipulate the graph, the LiteGraph documentation (at `doc/index.html` if you clone `https://github.com/jagenjo/litegraph.js`)
describes the functions you will need.

You can use `graph` to obtain details of nodes and links, for example:

```Javascript  theme={null}
const ComfyNode_object_for_my_node = app.graph._nodes_by_id(my_node_id) 
ComfyNode_object_for_my_node.inputs.forEach(input => {
    const link_id = input.link;
    if (link_id) {
        const LLink_object = app.graph.links[link_id]
        const id_of_upstream_node = LLink_object.origin_id
        // etc
    }
});
```

## LLink

The `LLink` object, accessible through `graph.links`, represents a single link in the graph, from node `link.origin_id` output slot `link.origin_slot`
to node `link.target_id` slot `link.target_slot`. It also has a string representing the data type, in `link.type`, and `link.id`.

`LLink`s are created in the `connect` method of a `LGraphNode` (of which `ComfyNode` is a subclass).

<Tip>Avoid creating your own LLink objects - use the LiteGraph functions instead.</Tip>

## ComfyNode

`ComfyNode` is a subclass of `LGraphNode`, and the LiteGraph documentation is therefore helpful for more generic
operations. However, Comfy has significantly extended the LiteGraph core behavior, and also does not make
use of all LiteGraph functionality.

<Tip>The description that follows applies to a normal node.
Group nodes, primitive nodes, notes, and redirect nodes have different properties.</Tip>

A `ComfyNode` object represents a node in the current workflow. It has a number of important properties
that you may wish to make use of, a very large number of functions that you may wish to use, or hijack to
modify behavior.

<Note>
  **Deprecated:** Hijacking prototype methods on `ComfyNode` or `LGraphNode` is deprecated and subject to change at any point in the near future. Use the official [extension hooks](/custom-nodes/js/javascript_hooks) where available, such as `getNodeMenuItems` for context menus. See the [Context Menu Migration Guide](/custom-nodes/js/context-menu-migration) for examples.
</Note>

To get a more complete sense of the node object, you may find it helpful to insert the following
code into your extension and place a breakpoint on the `console.log` command. When you then create a new node
you can use your favorite debugger to interrogate the node.

```Javascript  theme={null}
async nodeCreated(node) {
    console.log("nodeCreated")
}
```

### Properties

| property          | contents                                                                                                                            |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `bgcolor`         | The background color of the node, or undefined for the default                                                                      |
| `comfyClass`      | The Python class representing the node                                                                                              |
| `flags`           | A dictionary that may contain flags related to the state of the node. In particular, `flags.collapsed` is true for collapsed nodes. |
| `graph`           | A reference to the LGraph object                                                                                                    |
| `id`              | A unique id                                                                                                                         |
| `input_type`      | A list of the input types (eg "STRING", "MODEL", "CLIP" etc). Generally matches the Python INPUT\_TYPES                             |
| `inputs`          | A list of inputs (discussed below)                                                                                                  |
| `mode`            | Normally 0, set to 2 if the node is muted and 4 if the node is bypassed. Values of 1 and 3 are not used by Comfy                    |
| `order`           | The node's position in the execution order. Set by `LGraph.computeExecutionOrder()` when the prompt is submitted                    |
| `pos`             | The \[x,y] position of the node on the canvas                                                                                       |
| `properties`      | A dictionary containing `"Node name for S&R"`, used by LiteGraph                                                                    |
| `properties_info` | The type and default value of entries in `properties`                                                                               |
| `size`            | The width and height of the node on the canvas                                                                                      |
| `title`           | Display Title                                                                                                                       |
| `type`            | The unique name (from Python) of the node class                                                                                     |
| `widgets`         | A list of widgets (discussed below)                                                                                                 |
| `widgets_values`  | A list of the current values of widgets                                                                                             |

### Functions

There are a very large number of functions (85, last time I counted). A selection are listed below.
Most of these functions are unmodified from the LiteGraph core code.

#### Inputs, Outputs, Widgets

| function               | notes                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| Inputs / Outputs       | Most have output methods with the equivalent names: s/In/Out/                                      |
| `addInput`             | Create a new input, defined by name and type                                                       |
| `addInputs`            | Array version of `addInput`                                                                        |
| `findInputSlot`        | Find the slot index from the input name                                                            |
| `findInputSlotByType`  | Find an input matching the type. Options to prefer, or only use, free slots                        |
| `removeInput`          | By slot index                                                                                      |
| `getInputNode`         | Get the node connected to this input. The output equivalent is `getOutputNodes` and returns a list |
| `getInputLink`         | Get the LLink connected to this input. No output equivalent                                        |
| Widgets                |                                                                                                    |
| `addWidget`            | Add a standard Comfy widget                                                                        |
| `addCustomWidget`      | Add a custom widget (defined in the `getComfyWidgets` hook)                                        |
| `addDOMWidget`         | Add a widget defined by a DOM element                                                              |
| `convertWidgetToInput` | Convert a widget to an input if allowed by `isConvertableWidget` (in `widgetInputs.js`)            |

#### Connections

| function              | notes                                                                                             |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| `connect`             | Connect this node's output to another node's input                                                |
| `connectByType`       | Connect output to another node by specifying the type - connects to first available matching slot |
| `connectByTypeOutput` | Connect input to another node output by type                                                      |
| `disconnectInput`     | Remove any link into the input (specified by name or index)                                       |
| `disconnectOutput`    | Disconnect an output from a specified node's input                                                |
| `onConnectionChange`  | Called on each node. `side==1` if it's an input on this node                                      |
| `onConnectInput`      | Called *before* a connection is made. If this returns `false`, the connection is refused          |

#### Display

| function           | notes                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| `setDirtyCanvas`   | Specify that the foreground (nodes) and/or background (links and images) need to be redrawn            |
| `onDrawBackground` | Called with a `CanvasRenderingContext2D` object to draw the background. Used by Comfy to render images |
| `onDrawForeground` | Called with a `CanvasRenderingContext2D` object to draw the node.                                      |
| `getTitle`         | The title to be displayed.                                                                             |
| `collapse`         | Toggles the collapsed state of the node.                                                               |

<Warning>`collapse` is badly named; it *toggles* the collapsed state.
It takes a boolean parameter, which can be used to override
`node.collapsable === false`.</Warning>

#### Other

| function     | notes                                                              |
| ------------ | ------------------------------------------------------------------ |
| `changeMode` | Use to set the node to bypassed (`mode == 4`) or not (`mode == 0`) |

## Inputs and Widgets

Inputs and Widgets represent the two ways that data can be fed into a node. In general a widget can be
converted to an input, but not all inputs can be converted to a widget (as many datatypes can't be
entered through a UI element).

`node.inputs` is a list of the current inputs (colored dots on the left hand side of the node),
specifying their `.name`, `.type`, and `.link` (a reference to the connected `LLink` in `app.graph.links`).

If an input is a widget which has been converted, it also holds a reference to the, now inactive, widget in `.widget`.

`node.widgets` is a list of all widgets, whether or not they have been converted to an input. A widget has:

| property/function | notes                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| `callback`        | A function called when the widget value is changed                        |
| `last_y`          | The vertical position of the widget in the node                           |
| `name`            | The (unique within a node) widget name                                    |
| `options`         | As specified in the Python code (such as default, min, and max)           |
| `type`            | The name of the widget type (see below) in lowercase                      |
| `value`           | The current widget value. This is a property with `get` and `set` methods |

### Widget Types

`app.widgets` is a dictionary of currently registered widget types, keyed in the UPPER CASE version of the name of the type.
Build in Comfy widgets types include the self explanatory `BOOLEAN`, `INT`, and `FLOAT`,
as well as `STRING` (which comes in two flavours, single line and multiline),
`COMBO` for dropdown selection from a list, and `IMAGEUPLOAD`, used in Load Image nodes.

Custom widget types can be added by providing a `getCustomWidgets` method in your extension.

### Linked widgets

Widgets can also be linked - the built in behavior of `seed` and `control_after_generate`, for example.
A linked widget has `.type = 'base_widget_type:base_widget_name'`; so `control_after_generate` may have
type `int:seed`.

## Prompt

When you press the `Queue Prompt` button in Comfy, the `app.graphToPrompt()` method is called to convert the
current graph into a prompt that can be sent to the server.

`app.graphToPrompt` returns an object (referred to herein as `prompt`) with two properties, `output` and `workflow`.

### output

`prompt.output` maps from the `node_id` of each node in the graph to an object with two properties.

* `prompt.output[node_id].class_type`, the unique name of the custom node class, as defined in the Python code
* `prompt.output[node_id].inputs`, which contains the value of each input (or widget) as a map from the input name to:
  * the selected value, if it is a widget, or
  * an array containing (`upstream_node_id`, `upstream_node_output_slot`) if there is a link connected to the input, or
  * undefined, if it is a widget that has been converted to an input and is not connected
  * other unconnected inputs are not included in `.inputs`

<Tip>Note that the `upstream_node_id` in the array describing a connected input is represented as a string, not an integer.</Tip>

### workflow

`prompt.workflow` contains the following properties:

* `config` - a dictionary of additional configuration options (empty by default)
* `extra` - a dictionary containing extra information about the workflow. By default it contains:
  * `extra.ds` - describes the current view of the graph (`scale` and `offset`)
* `groups` - all groups in the workflow
* `last_link_id` - the id of the last link added
* `last_node_id` - the id of the last node added
* `links` - a list of all links in the graph. Each entry is an array of five integers and one string:
  * (`link_id`, `upstream_node_id`, `upstream_node_output_slot`, `downstream_node_id`, `downstream_node_input_slot`, `data type`)
* `nodes` - a list of all nodes in the graph. Each entry is a map of a subset of the properties of the node as described [above](#comfynode)
  * The following properties are included: `flags`, `id`, `inputs`, `mode`, `order`, `pos`, `properties`, `size`, `type`, `widgets_values`
  * In addition, unless a node has no outputs, there is an `outputs` property, which is a list of the outputs of the node, each of which contains:
    * `name` - the name of the output
    * `type` - the data type of the output
    * `links` - a list of the `link_id` of all links from this output (if there are no connections, may be an empty list, or null),
    * `shape` - the shape used to draw the output (default 3 for a dot)
    * `slot_index` - the slot number of the output
* `version` - the LiteGraph version number (at time of writing, `0.4`)

<Tip>`nodes.output` is absent for nodes with no outputs, not an empty list.</Tip>





# Settings

You can provide a settings object to ComfyUI that will show up when the user
opens the ComfyUI settings panel.

## Basic operation

### Add a setting

```javascript  theme={null}
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "My Extension",
    settings: [
        {
            id: "example.boolean",
            name: "Example boolean setting",
            type: "boolean",
            defaultValue: false,
        },
    ],
});
```

The `id` must be unique across all extensions and will be used to fetch values.

If you do not [provide a category](#categories), then the `id` will be split by
`.` to determine where it appears in the settings panel.

* If your `id` doesn't contain any `.` then it will appear in the "Other"
  category and your `id` will be used as the section heading.
* If your `id` contains at least one `.` then the leftmost part will be used
  as the setting category and the second part will be used as the section
  heading. Any further parts are ignored.

### Read a setting

```javascript  theme={null}
import { app } from "../../scripts/app.js";

if (app.extensionManager.setting.get('example.boolean')) {
    console.log("Setting is enabled.");
} else {
    console.log("Setting is disabled.");
}
```

### React to changes

The `onChange()` event handler will be called as soon as the user changes the
setting in the settings panel.

This will also be called when the extension is registered, on every page load.

```javascript  theme={null}
{
    id: "example.boolean",
    name: "Example boolean setting",
    type: "boolean",
    defaultValue: false,
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Write a setting

```javascript  theme={null}
import { app } from "../../scripts/app.js";

try {
    await app.extensionManager.setting.set("example.boolean", true);
} catch (error) {
    console.error(`Error changing setting: ${error}`);
}
```

### Extra configuration

The setting types are based on [PrimeVue](https://primevue.org/) components.
Props described in the PrimeVue documentation can be defined for ComfyUI
settings by adding them in an `attrs` field.

For instance, this adds increment/decrement buttons to a number input:

```javascript  theme={null}
{
    id: "example.number",
    name: "Example number setting",
    type: "number",
    defaultValue: 0,
    attrs: {
        showButtons: true,
    },
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

## Types

### Boolean

This shows an on/off toggle.

Based on the [ToggleSwitch PrimeVue
component](https://primevue.org/toggleswitch/).

```javascript  theme={null}
{
    id: "example.boolean",
    name: "Example boolean setting",
    type: "boolean",
    defaultValue: false,
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Text

This is freeform text.

Based on the [InputText PrimeVue component](https://primevue.org/inputtext/).

```javascript  theme={null}
{
    id: "example.text",
    name: "Example text setting",
    type: "text",
    defaultValue: "Foo",
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Number

This for entering numbers.

To allow decimal places, set the `maxFractionDigits` attribute to a number greater than zero.

Based on the [InputNumber PrimeVue
component](https://primevue.org/inputnumber/).

```javascript  theme={null}
{
    id: "example.number",
    name: "Example number setting",
    type: "number",
    defaultValue: 42,
    attrs: {
        showButtons: true,
        maxFractionDigits: 1,
    },
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Slider

This lets the user enter a number directly or via a slider.

Based on the [Slider PrimeVue component](https://primevue.org/slider/). Ranges
are not supported.

```javascript  theme={null}
{
    id: "example.slider",
    name: "Example slider setting",
    type: "slider",
    attrs: {
        min: -10,
        max: 10,
        step: 0.5,
    },
    defaultValue: 0,
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Combo

This lets the user pick from a drop-down list of values.

You can provide options either as a plain string or as an object with `text`
and `value` fields. If you only provide a plain string, then it will be used
for both.

You can let the user enter freeform text by supplying the `editable: true`
attribute, or search by supplying the `filter: true` attribute.

Based on the [Select PrimeVue component](https://primevue.org/select/). Groups
are not supported.

```javascript  theme={null}
{
    id: "example.combo",
    name: "Example combo setting",
    type: "combo",
    defaultValue: "first",
    options: [
        { text: "My first option", value: "first" },
        "My second option",
    ],
    attrs: {
        editable: true,
        filter: true,
    },
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Color

This lets the user select a color from a color picker or type in a hex
reference.

Note that the format requires six full hex digits - three digit shorthand does
not work.

Based on the [ColorPicker PrimeVue
component](https://primevue.org/colorpicker/).

```javascript  theme={null}
{
    id: "example.color",
    name: "Example color setting",
    type: "color",
    defaultValue: "ff0000",
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Image

This lets the user upload an image.

The setting will be saved as a [data
URL](https://developer.mozilla.org/en-US/docs/Web/URI/Schemes/data).

Based on the [FileUpload PrimeVue
component](https://primevue.org/fileupload/).

```javascript  theme={null}
{
    id: "example.image",
    name: "Example image setting",
    type: "image",
    onChange: (newVal, oldVal) => {
        console.log(`Setting was changed from ${oldVal} to ${newVal}`);
    },
}
```

### Hidden

Hidden settings aren't displayed in the settings panel, but you can read and
write to them from your code.

```javascript  theme={null}
{
    id: "example.hidden",
    name: "Example hidden setting",
    type: "hidden",
}
```

## Other

### Categories

You can specify the categorisation of your setting separately to the `id`.
This means you can change the categorisation and naming without changing the
`id` and losing the values that have already been set by users.

```javascript  theme={null}
{
    id: "example.boolean",
    name: "Example boolean setting",
    type: "boolean",
    defaultValue: false,
    category: ["Category name", "Section heading", "Setting label"],
}
```

### Tooltips

You can add extra contextual help with the `tooltip` field. This adds a small ℹ︎
icon after the field name that will show the help text when the user hovers
over it.

```javascript  theme={null}
{
    id: "example.boolean",
    name: "Example boolean setting",
    type: "boolean",
    defaultValue: false,
    tooltip: "This is some helpful information",
}
```








# Dialog API

The Dialog API provides standardized dialogs that work consistently across desktop and web environments. Extension authors will find the prompt and confirm methods most useful.

## Basic Usage

### Prompt Dialog

```javascript  theme={null}
// Show a prompt dialog
app.extensionManager.dialog.prompt({
  title: "User Input",
  message: "Please enter your name:",
  defaultValue: "User"
}).then(result => {
  if (result !== null) {
    console.log(`Input: ${result}`);
  }
});
```

### Confirm Dialog

```javascript  theme={null}
// Show a confirmation dialog
app.extensionManager.dialog.confirm({
  title: "Confirm Action",
  message: "Are you sure you want to continue?",
  type: "default"
}).then(result => {
  console.log(result ? "User confirmed" : "User cancelled");
});
```

## API Reference

### Prompt

```javascript  theme={null}
app.extensionManager.dialog.prompt({
  title: string,             // Dialog title
  message: string,           // Message/question to display
  defaultValue?: string      // Initial value in the input field (optional)
}).then((result: string | null) => {
  // result is the entered text, or null if cancelled
});
```

### Confirm

```javascript  theme={null}
app.extensionManager.dialog.confirm({
  title: string,             // Dialog title
  message: string,           // Message to display
  type?: "default" | "overwrite" | "delete" | "dirtyClose" | "reinstall", // Dialog type (optional)
  itemList?: string[],       // List of items to display (optional)
  hint?: string              // Hint text to display (optional)
}).then((result: boolean | null) => {
  // result is true if confirmed, false if denied, null if cancelled
});
```

For other specialized dialogs available in ComfyUI, extension authors can refer to the `dialogService.ts` file in the source code.






# Toast API

The Toast API provides a way to display non-blocking notification messages to users. These are useful for providing feedback without interrupting workflow.

## Basic Usage

### Simple Toast

```javascript  theme={null}
// Display a simple info toast
app.extensionManager.toast.add({
  severity: "info",
  summary: "Information",
  detail: "Operation completed successfully",
  life: 3000
});
```

### Toast Types

```javascript  theme={null}
// Success toast
app.extensionManager.toast.add({
  severity: "success",
  summary: "Success",
  detail: "Data saved successfully",
  life: 3000
});

// Warning toast
app.extensionManager.toast.add({
  severity: "warn",
  summary: "Warning",
  detail: "This action may cause problems",
  life: 5000
});

// Error toast
app.extensionManager.toast.add({
  severity: "error",
  summary: "Error",
  detail: "Failed to process request",
  life: 5000
});
```

### Alert Helper

```javascript  theme={null}
// Shorthand for creating an alert toast
app.extensionManager.toast.addAlert("This is an important message");
```

## API Reference

### Toast Message

```javascript  theme={null}
app.extensionManager.toast.add({
  severity?: "success" | "info" | "warn" | "error" | "secondary" | "contrast", // Message severity level (default: "info")
  summary?: string,         // Short title for the toast
  detail?: any,             // Detailed message content
  closable?: boolean,       // Whether user can close the toast (default: true)
  life?: number,            // Duration in milliseconds before auto-closing
  group?: string,           // Group identifier for managing related toasts
  styleClass?: any,         // Style class of the message
  contentStyleClass?: any   // Style class of the content
});
```

### Alert Helper

```javascript  theme={null}
app.extensionManager.toast.addAlert(message: string);
```

### Additional Methods

```javascript  theme={null}
// Remove a specific toast
app.extensionManager.toast.remove(toastMessage);

// Remove all toasts
app.extensionManager.toast.removeAll();
```




# About Panel Badges

The About Panel Badges API allows extensions to add custom badges to the ComfyUI about page. These badges can display information about your extension and contain links to documentation, source code, or other resources.

## Basic Usage

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  aboutPageBadges: [
    {
      label: "Documentation",
      url: "https://example.com/docs",
      icon: "pi pi-file"
    },
    {
      label: "GitHub",
      url: "https://github.com/username/repo",
      icon: "pi pi-github"
    }
  ]
});
```

## Badge Configuration

Each badge requires all of these properties:

```javascript  theme={null}
{
  label: string,           // Text to display on the badge
  url: string,             // URL to open when badge is clicked
  icon: string             // Icon class (e.g., PrimeVue icon)
}
```

## Icon Options

Badge icons use PrimeVue's icon set. Here are some commonly used icons:

* Documentation: `pi pi-file` or `pi pi-book`
* GitHub: `pi pi-github`
* External link: `pi pi-external-link`
* Information: `pi pi-info-circle`
* Download: `pi pi-download`
* Website: `pi pi-globe`
* Discord: `pi pi-discord`

For a complete list of available icons, refer to the [PrimeVue Icons documentation](https://primevue.org/icons/).

## Example

```javascript  theme={null}
app.registerExtension({
  name: "BadgeExample",
  aboutPageBadges: [
    {
      label: "Website",
      url: "https://example.com",
      icon: "pi pi-home"
    },
    {
      label: "Donate",
      url: "https://example.com/donate",
      icon: "pi pi-heart"
    },
    {
      label: "Documentation",
      url: "https://example.com/docs",
      icon: "pi pi-book"
    }
  ]
});
```

Badges appear in the About panel of the Settings dialog, which can be accessed via the gear icon in the top-right corner of the ComfyUI interface.










# Bottom Panel Tabs

The Bottom Panel Tabs API allows extensions to add custom tabs to the bottom panel of the ComfyUI interface. This is useful for adding features like logs, debugging tools, or custom panels.

## Basic Usage

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  bottomPanelTabs: [
    {
      id: "customTab",
      title: "Custom Tab",
      type: "custom",
      render: (el) => {
        el.innerHTML = '<div>This is my custom tab content</div>';
      }
    }
  ]
});
```

## Tab Configuration

Each tab requires an `id`, `title`, and `type`, along with a render function:

```javascript  theme={null}
{
  id: string,              // Unique identifier for the tab
  title: string,           // Display title shown on the tab
  type: string,            // Tab type (usually "custom")
  icon?: string,           // Icon class (optional)
  render: (element) => void // Function that populates the tab content
}
```

The `render` function receives a DOM element where you should insert your tab's content.

## Interactive Elements

You can add interactive elements like buttons:

```javascript  theme={null}
app.registerExtension({
  name: "InteractiveTabExample",
  bottomPanelTabs: [
    {
      id: "controlsTab",
      title: "Controls",
      type: "custom",
      render: (el) => {
        el.innerHTML = `
          <div style="padding: 10px;">
            <button id="runBtn">Run Workflow</button>
          </div>
        `;
        
        // Add event listeners
        el.querySelector('#runBtn').addEventListener('click', () => {
          app.queuePrompt();
        });
      }
    }
  ]
});
```

## Using React Components

You can mount React components in bottom panel tabs:

```javascript  theme={null}
// Import React dependencies in your extension
import React from "react";
import ReactDOM from "react-dom/client";

// Simple React component
function TabContent() {
  const [count, setCount] = React.useState(0);
  
  return (
    <div style={{ padding: "10px" }}>
      <h3>React Component</h3>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

// Register the extension with React content
app.registerExtension({
  name: "ReactTabExample",
  bottomPanelTabs: [
    {
      id: "reactTab",
      title: "React Tab",
      type: "custom",
      render: (el) => {
        const container = document.createElement("div");
        container.id = "react-tab-container";
        el.appendChild(container);
        
        // Mount React component
        ReactDOM.createRoot(container).render(
          <React.StrictMode>
            <TabContent />
          </React.StrictMode>
        );
      }
    }
  ]
});
```

## Standalone Registration

You can also register tabs outside of `registerExtension`:

```javascript  theme={null}
app.extensionManager.registerBottomPanelTab({
  id: "standAloneTab",
  title: "Stand-Alone Tab",
  type: "custom",
  render: (el) => {
    el.innerHTML = '<div>This tab was registered independently</div>';
  }
});
```




# Sidebar Tabs

The Sidebar Tabs API allows extensions to add custom tabs to the sidebar of the ComfyUI interface. This is useful for adding features that require persistent visibility and quick access.

## Basic Usage

```javascript  theme={null}
app.extensionManager.registerSidebarTab({
  id: "customSidebar",
  icon: "pi pi-compass",
  title: "Custom Tab",
  tooltip: "My Custom Sidebar Tab",
  type: "custom",
  render: (el) => {
    el.innerHTML = '<div>This is my custom sidebar content</div>';
  }
});
```

## Tab Configuration

Each tab requires several properties:

```javascript  theme={null}
{
  id: string,              // Unique identifier for the tab
  icon: string,            // Icon class for the tab button
  title: string,           // Title text for the tab
  tooltip?: string,        // Tooltip text on hover (optional)
  type: string,            // Tab type (usually "custom")
  render: (element) => void // Function that populates the tab content
}
```

The `render` function receives a DOM element where you should insert your tab's content.

## Icon Options

Sidebar tab icons can use various icon sets:

* PrimeVue icons: `pi pi-[icon-name]` (e.g., `pi pi-home`)
* Material Design icons: `mdi mdi-[icon-name]` (e.g., `mdi mdi-robot`)
* Font Awesome icons: `fa-[style] fa-[icon-name]` (e.g., `fa-solid fa-star`)

Ensure the corresponding icon library is loaded before using these icons.

## Stateful Tab Example

You can create tabs that maintain state:

```javascript  theme={null}
app.extensionManager.registerSidebarTab({
  id: "statefulTab",
  icon: "pi pi-list",
  title: "Notes",
  type: "custom",
  render: (el) => {
    // Create elements
    const container = document.createElement('div');
    container.style.padding = '10px';
    
    const notepad = document.createElement('textarea');
    notepad.style.width = '100%';
    notepad.style.height = '200px';
    notepad.style.marginBottom = '10px';
    
    // Load saved content if available
    const savedContent = localStorage.getItem('comfyui-notes');
    if (savedContent) {
      notepad.value = savedContent;
    }
    
    // Auto-save content
    notepad.addEventListener('input', () => {
      localStorage.setItem('comfyui-notes', notepad.value);
    });
    
    // Assemble the UI
    container.appendChild(notepad);
    el.appendChild(container);
  }
});
```

## Using React Components

You can mount React components in sidebar tabs:

```javascript  theme={null}
// Import React dependencies in your extension
import React from "react";
import ReactDOM from "react-dom/client";

// Register sidebar tab with React content
app.extensionManager.registerSidebarTab({
  id: "reactSidebar",
  icon: "mdi mdi-react",
  title: "React Tab",
  type: "custom",
  render: (el) => {
    const container = document.createElement("div");
    container.id = "react-sidebar-container";
    el.appendChild(container);
    
    // Define a simple React component
    function SidebarContent() {
      const [count, setCount] = React.useState(0);
      
      return (
        <div style={{ padding: "10px" }}>
          <h3>React Sidebar</h3>
          <p>Count: {count}</p>
          <button onClick={() => setCount(count + 1)}>
            Increment
          </button>
        </div>
      );
    }
    
    // Mount React component
    ReactDOM.createRoot(container).render(
      <React.StrictMode>
        <SidebarContent />
      </React.StrictMode>
    );
  }
});
```

For a real-world example of a React application integrated as a sidebar tab, check out the [ComfyUI-Copilot project on GitHub](https://github.com/AIDC-AI/ComfyUI-Copilot).

## Dynamic Content Updates

You can update sidebar content in response to graph changes:

```javascript  theme={null}
app.extensionManager.registerSidebarTab({
  id: "dynamicSidebar",
  icon: "pi pi-chart-line",
  title: "Stats",
  type: "custom",
  render: (el) => {
    const container = document.createElement('div');
    container.style.padding = '10px';
    el.appendChild(container);
    
    // Function to update stats
    function updateStats() {
      const stats = {
        nodes: app.graph._nodes.length,
        connections: Object.keys(app.graph.links).length
      };
      
      container.innerHTML = `
        <h3>Workflow Stats</h3>
        <ul>
          <li>Nodes: ${stats.nodes}</li>
          <li>Connections: ${stats.connections}</li>
        </ul>
      `;
    }
    
    // Initial update
    updateStats();
    
    // Listen for graph changes
    const api = app.api;
    api.addEventListener("graphChanged", updateStats);
    
    // Clean up listeners when tab is destroyed
    return () => {
      api.removeEventListener("graphChanged", updateStats);
    };
  }
});
```




# Selection Toolbox

The Selection Toolbox API allows extensions to add custom action buttons that appear when nodes are selected on the canvas. This provides quick access to context-sensitive commands for selected items (nodes, groups, etc.).

## Basic Usage

To add commands to the selection toolbox, your extension needs to:

1. Define commands with the standard [command interface](https://docs.comfy.org/custom-nodes/js/javascript_commands_keybindings)
2. Implement the `getSelectionToolboxCommands` method to specify which commands appear in the toolbox

Note: The `getSelectionToolboxCommands` method is called for each item in the selection set whenever a new selection is made.

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  commands: [
    {
      id: "my-extension.duplicate-special",
      label: "Duplicate Special",
      icon: "pi pi-copy",
      function: (selectedItem) => {
        // Your command logic here
        console.log("Duplicating selected nodes with special behavior");
      }
    }
  ],
  getSelectionToolboxCommands: (selectedItem) => {
    // Return array of command IDs to show in the toolbox
    return ["my-extension.duplicate-special"];
  }
});
```

## Command Definition

Commands for the selection toolbox use the standard ComfyUI command interface:

```javascript  theme={null}
{
  id: string,          // Unique identifier for the command
  label: string,       // Display text for the button tooltip
  icon?: string,       // Icon class for the button (optional)
  function: (selectedItem) => void  // Function executed when clicked
}
```

The `function` receives the selected item(s) as a parameter, allowing you to perform actions on the current selection.

## Icon Options

Selection toolbox buttons support the same icon libraries as other UI elements:

* PrimeVue icons: `pi pi-[icon-name]` (e.g., `pi pi-star`)
* Material Design icons: `mdi mdi-[icon-name]` (e.g., `mdi mdi-content-copy`)

## Dynamic Command Visibility

The `getSelectionToolboxCommands` method is called each time the selection changes, allowing you to show different commands based on what's selected:

```javascript  theme={null}
app.registerExtension({
  name: "ContextualCommands",
  commands: [
    {
      id: "my-ext.align-nodes",
      label: "Align Nodes",
      icon: "pi pi-align-left",
      function: () => {
        // Align multiple nodes
      }
    },
    {
      id: "my-ext.configure-single",
      label: "Configure",
      icon: "pi pi-cog",
      function: () => {
        // Configure single node
      }
    }
  ],
  getSelectionToolboxCommands: (selectedItem) => {
    const selectedItems = app.canvas.selectedItems;
    const itemCount = selectedItems ? selectedItems.size : 0;
    
    if (itemCount > 1) {
      // Show alignment command for multiple items
      return ["my-ext.align-nodes"];
    } else if (itemCount === 1) {
      // Show configuration for single item
      return ["my-ext.configure-single"];
    }
    
    return [];
  }
});
```

## Working with Selected Items

Access information about selected items through the app's canvas object. The `selectedItems` property is a Set that includes nodes, groups, and other canvas elements:

```javascript  theme={null}
app.registerExtension({
  name: "SelectionInfo",
  commands: [
    {
      id: "my-ext.show-info",
      label: "Show Selection Info",
      icon: "pi pi-info-circle",
      function: () => {
        const selectedItems = app.canvas.selectedItems;
        
        if (selectedItems && selectedItems.size > 0) {
          console.log(`Selected ${selectedItems.size} items`);
          
          // Iterate through selected items
          selectedItems.forEach(item => {
            if (item.type) {
              console.log(`Item: ${item.type} (ID: ${item.id})`);
            }
          });
        }
      }
    }
  ],
  getSelectionToolboxCommands: () => ["my-ext.show-info"]
});
```

## Complete Example

Here's a simple example showing various selection toolbox features:

```javascript  theme={null}
app.registerExtension({
  name: "SelectionTools",
  commands: [
    {
      id: "selection-tools.count",
      label: "Count Selection",
      icon: "pi pi-hashtag",
      function: () => {
        const count = app.canvas.selectedItems?.size || 0;
        app.extensionManager.toast.add({
          severity: "info",
          summary: "Selection Count",
          detail: `You have ${count} item${count !== 1 ? 's' : ''} selected`,
          life: 3000
        });
      }
    },
    {
      id: "selection-tools.copy-ids",
      label: "Copy IDs",
      icon: "pi pi-copy",
      function: () => {
        const items = Array.from(app.canvas.selectedItems || []);
        const ids = items.map(item => item.id).filter(id => id !== undefined);
        
        if (ids.length > 0) {
          navigator.clipboard.writeText(ids.join(', '));
          app.extensionManager.toast.add({
            severity: "success",
            summary: "Copied",
            detail: `Copied ${ids.length} IDs to clipboard`,
            life: 2000
          });
        }
      }
    },
    {
      id: "selection-tools.log-types",
      label: "Log Types",
      icon: "pi pi-info-circle",
      function: () => {
        const items = Array.from(app.canvas.selectedItems || []);
        const typeCount = {};
        
        items.forEach(item => {
          const type = item.type || 'unknown';
          typeCount[type] = (typeCount[type] || 0) + 1;
        });
        
        console.log("Selection types:", typeCount);
      }
    }
  ],
  
  getSelectionToolboxCommands: (selectedItem) => {
    const selectedItems = app.canvas.selectedItems;
    const itemCount = selectedItems ? selectedItems.size : 0;
    
    if (itemCount === 0) return [];
    
    const commands = ["selection-tools.count", "selection-tools.log-types"];
    
    // Only show copy command if items have IDs
    const hasIds = Array.from(selectedItems).some(item => item.id !== undefined);
    if (hasIds) {
      commands.push("selection-tools.copy-ids");
    }
    
    return commands;
  }
});
```

## Notes

* The selection toolbox must be enabled in settings: `Comfy.Canvas.SelectionToolbox`
* Commands must be defined in the `commands` array before being referenced in `getSelectionToolboxCommands`
* The toolbox automatically updates when the selection changes
* The `getSelectionToolboxCommands` method is called for each item in the selection set whenever a new selection is made
* Use `app.canvas.selectedItems` (a Set) to access all selected items including nodes, groups, and other canvas elements
* For backward compatibility, `app.canvas.selected_nodes` still exists but only contains nodes










# Commands and Keybindings

The Commands and Keybindings API allows extensions to register custom commands and associate them with keyboard shortcuts. This enables users to quickly trigger actions without using the mouse.

## Basic Usage

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  // Register commands
  commands: [
    {
      id: "myCommand",
      label: "My Command",
      function: () => {
        console.log("Command executed!");
      }
    }
  ],
  // Associate keybindings with commands
  keybindings: [
    {
      combo: { key: "k", ctrl: true },
      commandId: "myCommand"
    }
  ]
});
```

## Command Configuration

Each command requires an `id`, `label`, and `function`:

```javascript  theme={null}
{
  id: string,              // Unique identifier for the command
  label: string,           // Display name for the command
  function: () => void     // Function to execute when command is triggered
}
```

## Keybinding Configuration

Each keybinding requires a `combo` and `commandId`:

```javascript  theme={null}
{
  combo: {                 // Key combination
    key: string,           // The main key (single character or special key)
    ctrl?: boolean,        // Require Ctrl key (optional)
    shift?: boolean,       // Require Shift key (optional)
    alt?: boolean,         // Require Alt key (optional)
    meta?: boolean         // Require Meta/Command key (optional)
  },
  commandId: string        // ID of the command to trigger
}
```

### Special Keys

For non-character keys, use one of these values:

* Arrow keys: `"ArrowUp"`, `"ArrowDown"`, `"ArrowLeft"`, `"ArrowRight"`
* Function keys: `"F1"` through `"F12"`
* Other special keys: `"Escape"`, `"Tab"`, `"Enter"`, `"Backspace"`, `"Delete"`, `"Home"`, `"End"`, `"PageUp"`, `"PageDown"`

## Command Examples

```javascript  theme={null}
app.registerExtension({
  name: "CommandExamples",
  commands: [
    {
      id: "runWorkflow",
      label: "Run Workflow",
      function: () => {
        app.queuePrompt();
      }
    },
    {
      id: "clearWorkflow",
      label: "Clear Workflow",
      function: () => {
        if (confirm("Clear the workflow?")) {
          app.graph.clear();
        }
      }
    },
    {
      id: "saveWorkflow",
      label: "Save Workflow",
      function: () => {
        app.graphToPrompt().then(workflow => {
          const blob = new Blob([JSON.stringify(workflow)], {type: "application/json"});
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "workflow.json";
          a.click();
          URL.revokeObjectURL(url);
        });
      }
    }
  ]
});
```

## Keybinding Examples

```javascript  theme={null}
app.registerExtension({
  name: "KeybindingExamples",
  commands: [
    /* Commands defined above */
  ],
  keybindings: [
    // Ctrl+R to run workflow
    {
      combo: { key: "r", ctrl: true },
      commandId: "runWorkflow"
    },
    // Ctrl+Shift+C to clear workflow
    {
      combo: { key: "c", ctrl: true, shift: true },
      commandId: "clearWorkflow"
    },
    // Ctrl+S to save workflow
    {
      combo: { key: "s", ctrl: true },
      commandId: "saveWorkflow"
    },
    // F5 to run workflow (alternative)
    {
      combo: { key: "F5" },
      commandId: "runWorkflow"
    }
  ]
});
```

## Notes and Limitations

* Keybindings defined in the ComfyUI core cannot be overwritten by extensions. Check the core keybindings in these source files:
  * [Core Commands](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e76e9ec61a068fd2d89797762f08ee551e6d84a0/src/composables/useCoreCommands.ts)
  * [Core Menu Commands](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e76e9ec61a068fd2d89797762f08ee551e6d84a0/src/constants/coreMenuCommands.ts)
  * [Core Keybindings](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e76e9ec61a068fd2d89797762f08ee551e6d84a0/src/constants/coreKeybindings.ts)
  * [Reserved Key Combos](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e76e9ec61a068fd2d89797762f08ee551e6d84a0/src/constants/reservedKeyCombos.ts)

* Some key combinations are reserved by the browser (like Ctrl+F for search) and cannot be overridden

* If multiple extensions register the same keybinding, the behavior is undefined









# Topbar Menu

The Topbar Menu API allows extensions to add custom menu items to the ComfyUI's top menu bar. This is useful for providing access to advanced features or less frequently used commands.

## Basic Usage

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  // Define commands
  commands: [
    { 
      id: "myCommand", 
      label: "My Command", 
      function: () => { alert("Command executed!"); } 
    }
  ],
  // Add commands to menu
  menuCommands: [
    { 
      path: ["Extensions", "My Extension"], 
      commands: ["myCommand"] 
    }
  ]
});
```

Command definitions follow the same pattern as in the [Commands and Keybindings API](./javascript_commands_keybindings). See that page for more detailed information about defining commands.

## Command Configuration

Each command requires an `id`, `label`, and `function`:

```javascript  theme={null}
{
  id: string,              // Unique identifier for the command
  label: string,           // Display name for the command
  function: () => void     // Function to execute when command is triggered
}
```

## Menu Configuration

The `menuCommands` array defines where to place commands in the menu structure:

```javascript  theme={null}
{
  path: string[],          // Array representing menu hierarchy
  commands: string[]       // Array of command IDs to add at this location
}
```

The `path` array specifies the menu hierarchy. For example, `["File", "Export"]` would add commands to the "Export" submenu under the "File" menu.

## Menu Examples

### Adding to Existing Menus

```javascript  theme={null}
app.registerExtension({
  name: "MenuExamples",
  commands: [
    { 
      id: "saveAsImage", 
      label: "Save as Image", 
      function: () => { 
        // Code to save canvas as image
      } 
    },
    { 
      id: "exportWorkflow", 
      label: "Export Workflow", 
      function: () => { 
        // Code to export workflow
      } 
    }
  ],
  menuCommands: [
    // Add to File menu
    { 
      path: ["File"], 
      commands: ["saveAsImage", "exportWorkflow"] 
    }
  ]
});
```

### Creating Submenu Structure

```javascript  theme={null}
app.registerExtension({
  name: "SubmenuExample",
  commands: [
    { 
      id: "option1", 
      label: "Option 1", 
      function: () => { console.log("Option 1"); } 
    },
    { 
      id: "option2", 
      label: "Option 2", 
      function: () => { console.log("Option 2"); } 
    },
    { 
      id: "suboption1", 
      label: "Sub-option 1", 
      function: () => { console.log("Sub-option 1"); } 
    }
  ],
  menuCommands: [
    // Create a nested menu structure
    { 
      path: ["Extensions", "My Tools"], 
      commands: ["option1", "option2"] 
    },
    { 
      path: ["Extensions", "My Tools", "Advanced"], 
      commands: ["suboption1"] 
    }
  ]
});
```

### Multiple Menu Locations

You can add the same command to multiple menu locations:

```javascript  theme={null}
app.registerExtension({
  name: "MultiLocationExample",
  commands: [
    { 
      id: "helpCommand", 
      label: "Get Help", 
      function: () => { window.open("https://docs.example.com", "_blank"); } 
    }
  ],
  menuCommands: [
    // Add to Help menu
    { 
      path: ["Help"], 
      commands: ["helpCommand"] 
    },
    // Also add to Extensions menu
    { 
      path: ["Extensions"], 
      commands: ["helpCommand"] 
    }
  ]
});
```

Commands can work with other ComfyUI APIs like settings. For more information about the Settings API, see the [Settings API](./javascript_settings) documentation.










# Context Menu Migration Guide

This guide helps you migrate from the deprecated monkey-patching approach to the new context menu extension API.

The old approach of monkey-patching `LGraphCanvas.prototype.getCanvasMenuOptions` and `nodeType.prototype.getExtraMenuOptions` is deprecated:

<Tip>If you see deprecation warnings in your browser console, your extension is using the old API and should be migrated.</Tip>

## Migrating Canvas Menus

### Old Approach (Deprecated)

The old approach modified the prototype during extension setup:

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension",
  async setup() {
    // ❌ OLD: Monkey-patching the prototype
    const original = LGraphCanvas.prototype.getCanvasMenuOptions
    LGraphCanvas.prototype.getCanvasMenuOptions = function() {
      const options = original.apply(this, arguments)

      options.push(null) // separator
      options.push({
        content: "My Custom Action",
        callback: () => {
          console.log("Action triggered")
        }
      })

      return options
    }
  }
})
```

### New Approach (Recommended)

The new approach uses a dedicated extension hook:

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension",
  // ✅ NEW: Use the getCanvasMenuItems hook
  getCanvasMenuItems(canvas) {
    return [
      null, // separator
      {
        content: "My Custom Action",
        callback: () => {
          console.log("Action triggered")
        }
      }
    ]
  }
})
```

### Key Differences

| Old Approach               | New Approach                     |
| -------------------------- | -------------------------------- |
| Modified in `setup()`      | Uses `getCanvasMenuItems()` hook |
| Wraps existing function    | Returns menu items directly      |
| Modifies `options` array   | Returns new array                |
| Canvas accessed via `this` | Canvas passed as parameter       |

## Migrating Node Menus

### Old Approach (Deprecated)

The old approach modified the node type prototype:

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeType.comfyClass === "KSampler") {
      // ❌ OLD: Monkey-patching the node prototype
      const original = nodeType.prototype.getExtraMenuOptions
      nodeType.prototype.getExtraMenuOptions = function(canvas, options) {
        original?.apply(this, arguments)

        options.push({
          content: "Randomize Seed",
          callback: () => {
            const seedWidget = this.widgets.find(w => w.name === "seed")
            if (seedWidget) {
              seedWidget.value = Math.floor(Math.random() * 1000000)
            }
          }
        })
      }
    }
  }
})
```

### New Approach (Recommended)

The new approach uses a dedicated extension hook:

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension",
  // ✅ NEW: Use the getNodeMenuItems hook
  getNodeMenuItems(node) {
    const items = []

    // Add items only for specific node types
    if (node.comfyClass === "KSampler") {
      items.push({
        content: "Randomize Seed",
        callback: () => {
          const seedWidget = node.widgets.find(w => w.name === "seed")
          if (seedWidget) {
            seedWidget.value = Math.floor(Math.random() * 1000000)
          }
        }
      })
    }

    return items
  }
})
```

### Key Differences

| Old Approach                          | New Approach                         |
| ------------------------------------- | ------------------------------------ |
| Modified in `beforeRegisterNodeDef()` | Uses `getNodeMenuItems()` hook       |
| Type-specific via `if` check          | Type-specific via `if` check in hook |
| Modifies `options` array              | Returns new array                    |
| Node accessed via `this`              | Node passed as parameter             |

## Common Patterns

### Conditional Menu Items

Both approaches support conditional items, but the new API is cleaner:

```javascript  theme={null}
// ✅ NEW: Clean conditional logic
getCanvasMenuItems(canvas) {
  const items = []

  if (canvas.selectedItems.size > 0) {
    items.push({
      content: `Process ${canvas.selectedItems.size} Selected Nodes`,
      callback: () => {
        // Process nodes
      }
    })
  }

  return items
}
```

### Adding Separators

Separators are added the same way in both approaches:

```javascript  theme={null}
getCanvasMenuItems(canvas) {
  return [
    null, // Separator (horizontal line)
    {
      content: "My Action",
      callback: () => {}
    }
  ]
}
```

### Creating Submenus

The recommended way to create submenus is using the declarative `submenu` property:

```javascript  theme={null}
getNodeMenuItems(node) {
  return [
    {
      content: "Advanced Options",
      submenu: {
        options: [
          { content: "Option 1", callback: () => {} },
          { content: "Option 2", callback: () => {} }
        ]
      }
    }
  ]
}
```

This declarative approach is cleaner and matches the patterns used throughout the ComfyUI codebase.

<Tip>While a callback-based approach with `has_submenu: true` and `new LiteGraph.ContextMenu()` is also supported, the declarative `submenu` property is preferred for better maintainability.</Tip>

### Accessing State

```javascript  theme={null}
// ✅ NEW: State access is clearer
getCanvasMenuItems(canvas) {
  // Access canvas properties
  const selectedCount = canvas.selectedItems.size
  const graphMousePos = canvas.graph_mouse

  return [/* menu items */]
}

getNodeMenuItems(node) {
  // Access node properties
  const nodeType = node.comfyClass
  const isDisabled = node.mode === 2
  const widgets = node.widgets

  return [/* menu items */]
}
```

## Troubleshooting

### How to Identify Old API Usage

Look for these patterns in your code:

```javascript  theme={null}
// ❌ Signs of old API:
LGraphCanvas.prototype.getCanvasMenuOptions = function() { /* ... */ }
nodeType.prototype.getExtraMenuOptions = function() { /* ... */ }
```

### Understanding Deprecation Warnings

If you see this warning in the console:

```
[DEPRECATED] Monkey-patching getCanvasMenuOptions is deprecated. (Extension: "MyExtension")
Please use the new context menu API instead.
See: https://docs.comfy.org/custom-nodes/js/context-menu-migration
```

Your extension is using the old approach and should be migrated.

### Verifying Migration Success

After migration:

1. Remove all prototype modifications from `setup()` and `beforeRegisterNodeDef()`
2. Add `getCanvasMenuItems()` and/or `getNodeMenuItems()` hooks
3. Test that your menu items still appear correctly
4. Verify no deprecation warnings appear in the console

### Complete Migration Example

**Before:**

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  async setup() {
    const original = LGraphCanvas.prototype.getCanvasMenuOptions
    LGraphCanvas.prototype.getCanvasMenuOptions = function() {
      const options = original.apply(this, arguments)
      options.push({ content: "Action", callback: () => {} })
      return options
    }
  },
  async beforeRegisterNodeDef(nodeType) {
    if (nodeType.comfyClass === "KSampler") {
      const original = nodeType.prototype.getExtraMenuOptions
      nodeType.prototype.getExtraMenuOptions = function(_, options) {
        original?.apply(this, arguments)
        options.push({ content: "Node Action", callback: () => {} })
      }
    }
  }
})
```

**After:**

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  getCanvasMenuItems(canvas) {
    return [
      { content: "Action", callback: () => {} }
    ]
  },
  getNodeMenuItems(node) {
    if (node.comfyClass === "KSampler") {
      return [
        { content: "Node Action", callback: () => {} }
      ]
    }
    return []
  }
})
```

## Additional Resources

* [Annotated Examples](./javascript_examples) - More examples using the new API
* [Extension Hooks](./javascript_hooks) - Complete list of available extension hooks
* [Commands and Keybindings](./javascript_commands_keybindings) - Add keyboard shortcuts to your menu actions




# Subgraphs

> Working with subgraphs in ComfyUI extensions: node IDs, graph traversal, events, widget promotion, and cleanup.

## Overview

Subgraphs let users group nodes into reusable, nestable components. Each subgraph is its own `LGraph` with a UUID. For the user-facing guide, see [Subgraphs](/interface/features/subgraph).

## Node Identifiers

ComfyUI uses three distinct node identifier types. Using the wrong one causes silent failures.

| Type         | Format                                | Used for                                                    |
| ------------ | ------------------------------------- | ----------------------------------------------------------- |
| `node.id`    | `42` (number)                         | Local to its immediate graph level. `graph.getNodeById(id)` |
| Execution ID | `"1:2:3"` (colon-separated string)    | Backend progress messages, `UNIQUE_ID`                      |
| Locator ID   | `"<uuid>:<localId>"` or `"<localId>"` | UI state: badges, errors, images                            |

To construct a node's locator ID from within an extension:

```javascript  theme={null}
function getLocatorId(node) {
  const graphId = node.graph?.id
  return graphId ? `${graphId}:${node.id}` : String(node.id)
}
```

## Traversing Nodes

### Current layer only

```javascript  theme={null}
for (const node of app.graph.nodes) {
  console.log(node.id, node.type)
}
```

### All nodes recursively

To walk into nested subgraphs, use a recursive helper that calls a callback on every node:

```javascript  theme={null}
function walkGraph(graph, callback) {
  for (const node of graph.nodes ?? []) {
    callback(node, graph)
    if (node.subgraph) walkGraph(node.subgraph, callback)
  }
}
```

Full example:

```javascript  theme={null}
import { app } from "../../scripts/app.js"

function walkGraph(graph, callback) {
  for (const node of graph.nodes ?? []) {
    callback(node, graph)
    if (node.subgraph) walkGraph(node.subgraph, callback)
  }
}

app.registerExtension({
  name: "MyExtension.SubgraphWalker",
  async afterConfigureGraph() {
    walkGraph(app.graph, (node, graph) => {
      console.log(`[${graph.id ?? "root"}] node ${node.id}: ${node.type}`)
    })
  }
})
```

## Root vs Active Graph

| You want to...                       | Use                 |
| ------------------------------------ | ------------------- |
| Operate on all nodes in the workflow | `app.graph` (root)  |
| Operate on only the visible layer    | `app.canvas?.graph` |
| Access a specific subgraph           | `someNode.subgraph` |

```javascript  theme={null}
// All nodes (including nested subgraphs)
walkGraph(app.graph, (node) => { /* ... */ })

// Only nodes the user currently sees
for (const node of app.canvas?.graph?.nodes ?? []) { /* ... */ }
```

## Events

### Subgraph-level events

Dispatched on `subgraph.events`:

| Event             | Payload                               | When                            |
| ----------------- | ------------------------------------- | ------------------------------- |
| `widget-promoted` | `{ widget, subgraphNode }`            | Widget promoted to parent node  |
| `widget-demoted`  | `{ widget, subgraphNode }`            | Widget removed from parent node |
| `input-added`     | `{ input }`                           | Input slot added                |
| `removing-input`  | `{ input, index }`                    | Input slot being removed        |
| `output-added`    | `{ output }`                          | Output slot added               |
| `removing-output` | `{ output, index }`                   | Output slot being removed       |
| `renaming-input`  | `{ input, index, oldName, newName }`  | Input slot renamed              |
| `renaming-output` | `{ output, index, oldName, newName }` | Output slot renamed             |

### Canvas-level events

Dispatched on `app.canvas.canvas` (the HTML canvas element):

| Event                | Payload                                | When                              |
| -------------------- | -------------------------------------- | --------------------------------- |
| `subgraph-opened`    | `{ subgraph, closingGraph, fromNode }` | User navigates into a subgraph    |
| `subgraph-converted` | `{ subgraphNode }`                     | Selection converted to a subgraph |

### Listening pattern

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension.SubgraphEvents",
  async setup() {
    app.canvas.canvas.addEventListener("subgraph-opened", (e) => {
      const { subgraph, fromNode } = e.detail
      console.log(`Opened subgraph from node ${fromNode.id}`)
    })
  }
})
```

## Widget Promotion

When a `SubgraphInput` connects to a widget inside a subgraph, a copy of that widget appears on the parent subgraph node. This fires `widget-promoted`. Removing the connection fires `widget-demoted`.

<Warning>
  Widget promotion behavior is still evolving and may change in future releases.
</Warning>

```javascript  theme={null}
import { app } from "../../scripts/app.js"

function walkGraph(graph, callback) {
  for (const node of graph.nodes ?? []) {
    callback(node, graph)
    if (node.subgraph) walkGraph(node.subgraph, callback)
  }
}

app.registerExtension({
  name: "MyExtension.WidgetPromotion",
  async afterConfigureGraph() {
    walkGraph(app.graph, (node) => {
      if (!node.subgraph) return
      if (node._promCleanup) node._promCleanup.abort()
      const controller = new AbortController()
      node._promCleanup = controller
      const { signal } = controller

      node.subgraph.events.addEventListener("widget-promoted", (e) => {
        console.log(`Widget "${e.detail.widget.name}" promoted`)
      }, { signal })

      node.subgraph.events.addEventListener("widget-demoted", (e) => {
        console.log(`Widget "${e.detail.widget.name}" demoted`)
      }, { signal })

      const origRemoved = node.onRemoved
      node.onRemoved = function () {
        controller.abort()
        origRemoved?.apply(this, arguments)
      }
    })
  }
})
```

## Cleanup

Use an `AbortController` to clean up all event listeners when a node is removed.

```javascript  theme={null}
import { app } from "../../scripts/app.js"

app.registerExtension({
  name: "MyExtension.Cleanup",
  async nodeCreated(node) {
    if (!node.subgraph) return

    const controller = new AbortController()
    const { signal } = controller

    node.subgraph.events.addEventListener("input-added", (e) => {
      console.log(`Input added: ${e.detail.input.name}`)
    }, { signal })

    node.subgraph.events.addEventListener("removing-input", (e) => {
      console.log(`Input removing: ${e.detail.input.name}`)
    }, { signal })

    const origRemoved = node.onRemoved
    node.onRemoved = function () {
      controller.abort()
      origRemoved?.apply(this, arguments)
    }
  }
})
```

<Tip>
  `onRemoved` can also fire during subgraph conversion, not just deletion. Guard teardown logic if you need to preserve state across restructuring.
</Tip>

## See Also

* [Subgraphs (User Guide)](/interface/features/subgraph)
* [Extension Hooks](/custom-nodes/js/javascript_hooks)







# Annotated Examples

A growing collection of fragments of example code...

## Right click menus

### Background menu

The main background menu (right-click on the canvas) is generated by a call to
`LGraphCanvas.getCanvasMenuOptions`. The standard way of editing this is to implement the `getCanvasMenuItems` method on your extension:

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  getCanvasMenuItems(canvas) {
    const items = []
    items.push(null) // inserts a divider
    items.push({
      content: "The text for the menu",
      callback: async () => {
        // do whatever
      }
    })
    return items
  }
});
```

### Node menu

When you right click on a node, the menu is similarly generated by `node.getExtraMenuOptions`.
The standard way is to implement the `getNodeMenuItems` method on your extension:

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  getNodeMenuItems(node) {
    const items = []

    // You can filter by node type if needed
    if (node.comfyClass === "MyNodeClass") {
      items.push({
        content: "Do something fun",
        callback: async () => {
          // fun thing
        }
      })
    }

    return items
  }
});
```

### Submenus

If you want a submenu, use the `submenu` property with an `options` array:

```javascript  theme={null}
app.registerExtension({
  name: "MyExtension",
  getCanvasMenuItems(canvas) {
    const items = []
    items.push({
      content: "Menu with options",
      submenu: {
        options: [
          {
            content: "option 1",
            callback: (v) => {
              // do something with v
            }
          },
          {
            content: "option 2",
            callback: (v) => {
              // do something with v
            }
          },
          {
            content: "option 3",
            callback: (v) => {
              // do something with v
            }
          }
        ]
      }
    })
    return items
  }
});
```

## Capture UI events

This works just like you'd expect - find the UI element in the DOM and
add an eventListener. `setup()` is a good place to do this, since the page
has fully loaded. For instance, to detect a click on the 'Queue' button:

```Javascript  theme={null}
function queue_button_pressed() { console.log("Queue button was pressed!") }
document.getElementById("queue-button").addEventListener("click", queue_button_pressed);
```

## Detect when a workflow starts

This is one of many `api` events:

```javascript  theme={null}
import { api } from "../../scripts/api.js";
/* in setup() */
    function on_execution_start() { 
        /* do whatever */
    }
    api.addEventListener("execution_start", on_execution_start);
```

## Detect an interrupted workflow

<Note>
  **Deprecated:** The API hijacking pattern shown below is deprecated and subject to change at any point in the near future. Use the official [extension hooks](/custom-nodes/js/javascript_hooks) and API event listeners where available.
</Note>

A simple example of hijacking the api:

```Javascript  theme={null}
import { api } from "../../scripts/api.js";
/* in setup() */
    const original_api_interrupt = api.interrupt;
    api.interrupt = function () {
        /* Do something before the original method is called */
        original_api_interrupt.apply(this, arguments);
        /* Or after */
    }
```

## Catch clicks on your node

<Note>
  **Deprecated:** The node method hijacking pattern shown below is deprecated and subject to change at any point in the near future. Use the official [extension hooks](/custom-nodes/js/javascript_hooks) where available.
</Note>

`node` has a mouseDown method you can hijack.
This time we're careful to pass on any return value.

```javascript  theme={null}
async nodeCreated(node) {
    if (node?.comfyClass === "My Node Name") {
        const original_onMouseDown = node.onMouseDown;
        node.onMouseDown = function( e, pos, canvas ) {
            alert("ouch!");
            return original_onMouseDown?.apply(this, arguments);
        }        
    }
}
```




# ComfyUI Custom Nodes i18n Support

> Learn how to add multi-language support for ComfyUI custom nodes

If you want to add support for multiple languages, you can refer to this document to learn how to implement multi-language support.

Currently, ComfyUI supports the following languages:

* English（en）
* Chinese (Simplified)（zh）
* Chinese (Traditional)（zh-TW）
* French（fr）
* Korean（ko）
* Russian（ru）
* Spanish（es）
* Japanese（ja）
* Arabic（ar）

Custom node i18n demo: [comfyui-wiki/ComfyUI-i18n-demo](https://github.com/comfyui-wiki/ComfyUI-i18n-demo)

## Directory Structure

Create a `locales` folder under your custom node, which supports multiple types of translation files:

```bash  theme={null}
your_custom_node/
├── __init__.py
├── your_node.py
└── locales/                   # i18n support folder
    ├── en/                    # English translations (recommended as the base)
    │   ├── main.json          # General English translation content
    │   ├── nodeDefs.json      # English node definition translations
    │   ├── settings.json      # Optional: settings interface translations
    │   └── commands.json      # Optional: command translations
    ├── zh/                    # Chinese translation files
    │   ├── nodeDefs.json      # Chinese node definition translations
    │   ├── main.json          # General Chinese translation content
    │   ├── settings.json      # Chinese settings interface translations
    │   └── commands.json      # Chinese command translations
    ├──...

```

## nodeDefs.json - Node Definition Translation

For example, here is a Python definition example of an [i18n-demo](https://github.com/comfyui-wiki/ComfyUI-i18n-demo) node:

```python  theme={null}
class I18nTextProcessor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "Hello World!",
                    "tooltip": "The original text content to be processed"
                }),
                "operation": (["uppercase", "lowercase", "reverse", "add_prefix"], {
                    "default": "uppercase",
                    "tooltip": "The text processing operation to be executed"
                }),
                "count": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "The number of times to repeat the operation"
                }),
            },
            "optional": {
                "prefix": ("STRING", {
                    "default": "[I18N] ",
                    "multiline": False,
                    "tooltip": "The prefix to add to the text"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("processed_text",)
    FUNCTION = "process_text"
    CATEGORY = "I18n Demo"
    DESCRIPTION = "A simple i18n demo node that demonstrates text processing with internationalization support"

    def process_text(self, text, operation, count, prefix=""):
        try:
            result = text
            
            for _ in range(count):
                if operation == "uppercase":
                    result = result.upper()
                elif operation == "lowercase":
                    result = result.lower()
                elif operation == "reverse":
                    result = result[::-1]
                elif operation == "add_prefix":
                    result = prefix + result
            
            return (result,)
        except Exception as e:
            print(f"I18nTextProcessor error: {e}")
            return (f"Error: {str(e)}",)
```

Then the corresponding localized support nodeDefs.json file content should include:

```json  theme={null}
{
  "I18nTextProcessor": {
    "display_name": "I18n Text Processor",
    "description": "A simple i18n demo node that demonstrates text processing with internationalization support",
    "inputs": {
      "text": {
        "name": "Text Input",
        "tooltip": "The original text content to be processed"
      },
      "operation": {
        "name": "Operation Type",
        "tooltip": "The text processing operation to be executed",
        "options": {
          "uppercase": "To Uppercase",
          "lowercase": "To Lowercase",
          "reverse": "Reverse Text",
          "add_prefix": "Add Prefix"
        }
      },
      "count": {
        "name": "Repeat Count",
        "tooltip": "The number of times to repeat the operation"
      },
      "prefix": {
        "name": "Prefix Text",
        "tooltip": "The prefix to add to the text"
      }
    },
    "outputs": {
      "0": {
        "name": "Processed Text",
        "tooltip": "The final processed text result"
      }
    }
  }
}
```

For the node output part, the corresponding output index is used instead of the output name, for example, the first output should be `0`, the second output should be `1`, and so on.

## Menu Settings

For example, in the i18n-demo custom node, we registered the following two menu settings:

```javascript  theme={null}
app.registerExtension({
    name: "I18nDemo",
    settings: [
        {
            id: "I18nDemo.EnableDebugMode",
            category: ["I18nDemo","DebugMode"], // This matches the settingsCategories key in main.json
            name: "Enable Debug Mode", // Will be overridden by translation
            tooltip: "Show debug information in console for i18n demo nodes", // Will be overridden by translation
            type: "boolean",
            defaultValue: false,
            experimental: true,
            onChange: (value) => {
                console.log("I18n Demo:", value ? "Debug mode enabled" : "Debug mode disabled");
            }
        },
        {
            id: "I18nDemo.DefaultTextOperation",
            category: ["I18nDemo","DefaultTextOperation"], // This matches the settingsCategories key in main.json
            name: "Default Text Operation", // Will be overridden by translation
            tooltip: "Default operation for text processor node", // Will be overridden by translation
            type: "combo",
            options: ["uppercase", "lowercase", "reverse", "add_prefix"],
            defaultValue: "uppercase",
            experimental: true
        }
    ],
    })
```

If you need to add corresponding internationalization support, for the menu category, you need to add it in the `main.json` file:

```json  theme={null}
{
  "settingsCategories": {
    "I18nDemo": "I18n Demo",
    "DebugMode": "Debug Mode",
    "DefaultTextOperation": "Default Text Operation"
  }
}
```

For the translation of the corresponding setting items, it is recommended to update them separately in the `settings.json` file, for example:

```json  theme={null}
{
  "I18nDemo_EnableDebugMode": {
    "name": "Enable Debug Mode",
    "tooltip": "Show debug information in console for i18n demo nodes"
  },
  "I18nDemo_DefaultTextOperation": {
    "name": "Default Text Operation",
    "tooltip": "Default operation for text processor node",
    "options": {
      "uppercase": "Uppercase",
      "lowercase": "Lowercase",
      "reverse": "Reverse",
      "add_prefix": "Add Prefix"
    }
  }
}
```

Note that the name of the corresponding translation key should replace the `.` in the original id with `_`, for example:

```
"I18nDemo.EnableDebugMode" -> "I18nDemo_EnableDebugMode"
```

## Custom Frontend Component Localization Support

\[To be updated]










# V3 Migration

> How to migrate your existing V1 nodes to the new V3 schema.

## Overview

The ComfyUI V3 schema introduces a more organized way of defining nodes, and future extensions to node features will only be added to V3 schema. You can use this guide to help you migrate your existing V1 nodes to the new V3 schema.

## Core Concepts

The V3 schema is kept on the new versioned Comfy API, meaning future revisions to the schema will be backwards compatible. `comfy_api.latest` will point to the latest numbered API that is still under development; the version before latest is what can be considered 'stable'. Version `v0_0_2` is the current (and first) API version so more changes will be made to it without warning. Once it is considered stable, a new version `v0_0_3` will be created for `latest` to point at.

```python  theme={null}
# use latest ComfyUI API
from comfy_api.latest import ComfyExtension, io, ui

# use a specific version of ComfyUI API
from comfy_api.v0_0_2 import ComfyExtension, io, ui
```

### V1 vs V3 Architecture

The biggest changes in V3 schema are:

* Inputs and Outputs defined by objects instead of a dictionary.
* The execution method is fixed to the name 'execute' and is a class method.
* `def comfy_entrypoint()` function that returns a ComfyExtension object defines exposed nodes instead of NODE\_CLASS\_MAPPINGS/NODE\_DISPLAY\_NAME\_MAPPINGS
* Node objects do not expose 'state' - `def __init__(self)` will have no effect on what is exposed in the node's functions, as all of them are class methods. The node class is sanitized before execution as well.

#### V1 (Legacy)

```python  theme={null}
class MyNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {...}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "my_category"

    def execute(self, ...):
        return (result,)

NODE_CLASS_MAPPINGS = {"MyNode": MyNode}
```

#### V3 (Modern)

```python  theme={null}
from comfy_api.latest import ComfyExtension, io

class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="MyNode",
            display_name="My Node",
            category="my_category",
            inputs=[...],
            outputs=[...]
        )

    @classmethod
    def execute(cls, ...) -> io.NodeOutput:
        return io.NodeOutput(result)

class MyExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [MyNode]

async def comfy_entrypoint() -> ComfyExtension:
    return MyExtension()
```

## Migration Steps

Going from V1 to V3 should be simple in most cases and is simply a syntax change.

### Step 1: Change Base Class

All V3 Schema nodes should inherit from `ComfyNode`. Multiple layers of inheritance are okay as long as at the top of the chain there is a `ComfyNode` parent.

**V1:**

```python  theme={null}
class Example:
    def __init__(self):
        pass
```

**V3:**

```python  theme={null}
from comfy_api.latest import io

class Example(io.ComfyNode):
    # No __init__ needed
```

### Step 2: Convert INPUT\_TYPES to define\_schema

Node properties like node id, display name, category, etc. that were assigned in different places in code such as dictionaries and class properties are now kept together via the `Schema` class.

The `define_schema(cls)` function is expected to return a `Schema` object in much the same way INPUT\_TYPES(s) worked in V1.

Supported core Input/Output types are stored and documented in `comfy_api/{version}` in `_io.py`, which is namespaced as `io` by default. Since Inputs/Outputs are defined by classes now instead of dictionaries or strings, custom types are supported by either defining your own class or using the helper function `Custom` in `io`.

Custom types are elaborated on in a section further below.

A type class has the following properties:

* `class Input` for Inputs (i.e. `Model.Input(...)`)
* `class Output` for Outputs (i.e. `Model.Output(...)`). Note that all types may not support being an output.
* `Type` for getting a typehint of the type (i.e. `Model.Type`). Note that some typehints are just `any`, which may be updated in the future. These typehints are not enforced and just act as useful documentation.

**V1:**

```python  theme={null}
@classmethod
def INPUT_TYPES(s):
    return {
        "required": {
            "image": ("IMAGE",),
            "int_field": ("INT", {
                "default": 0,
                "min": 0,
                "max": 4096,
                "step": 64,
                "display": "number"
            }),
            "string_field": ("STRING", {
                "multiline": False,
                "default": "Hello"
            }),
            # V1 handling of arbitrary types
            "custom_field": ("MY_CUSTOM_TYPE",),
        },
        "optional": {
            "mask": ("MASK",)
        }
    }
```

**V3:**

```python  theme={null}
@classmethod
def define_schema(cls) -> io.Schema:
    return io.Schema(
        node_id="Example",
        display_name="Example Node",
        category="examples",
        description="Node description here",
        inputs=[
            io.Image.Input("image"),
            io.Int.Input("int_field",
                default=0,
                min=0,
                max=4096,
                step=64,
                display_mode=io.NumberDisplay.number
            ),
            io.String.Input("string_field",
                default="Hello",
                multiline=False
            ),
            # V3 handling of arbitrary types
            io.Custom("my_custom_type").Input("custom_input"),
            io.Mask.Input("mask", optional=True)
        ],
        outputs=[
            io.Image.Output()
        ]
    )
```

### Step 3: Update Execute Method

All execution functions in v3 are named `execute` and are class methods.

**V1:**

```python  theme={null}
def test(self, image, string_field, int_field):
    # Process
    image = 1.0 - image
    return (image,)
```

**V3:**

```python  theme={null}
@classmethod
def execute(cls, image, string_field, int_field) -> io.NodeOutput:
    # Process
    image = 1.0 - image

    # Return with optional UI preview
    return io.NodeOutput(image, ui=ui.PreviewImage(image, cls=cls))
```

### Step 4: Convert Node Properties

Here are some examples of property names; see the source code in `comfy_api.latest._io` for more details.

| V1 Property    | V3 Schema Field             | Notes                       |
| -------------- | --------------------------- | --------------------------- |
| `RETURN_TYPES` | `outputs` in Schema         | List of Output objects      |
| `RETURN_NAMES` | `display_name` in Output    | Per-output display names    |
| `FUNCTION`     | Always `execute`            | Method name is standardized |
| `CATEGORY`     | `category` in Schema        | String value                |
| `OUTPUT_NODE`  | `is_output_node` in Schema  | Boolean flag                |
| `DEPRECATED`   | `is_deprecated` in Schema   | Boolean flag                |
| `EXPERIMENTAL` | `is_experimental` in Schema | Boolean flag                |

### Step 5: Handle Special Methods

The same special methods are supported as in v1, but either lowercased or renamed entirely to be more clear. Their usage remains the same.

#### Validation (V1 → V3)

The input validation function was renamed to `validate_inputs`.

**V1:**

```python  theme={null}
@classmethod
def VALIDATE_INPUTS(s, **kwargs):
    # Validation logic
    return True
```

**V3:**

```python  theme={null}
@classmethod
def validate_inputs(cls, **kwargs) -> bool | str:
    # Return True if valid, error string if not
    if error_condition:
        return "Error message"
    return True
```

#### Lazy Evaluation (V1 → V3)

The `check_lazy_status` function is class method, remains the same otherwise.

**V1:**

```python  theme={null}
def check_lazy_status(self, image, string_field, ...):
    if condition:
        return ["string_field"]
    return []
```

**V3:**

```python  theme={null}
@classmethod
def check_lazy_status(cls, image, string_field, ...):
    if condition:
        return ["string_field"]
    return []
```

#### Cache Control (V1 → V3)

The functionality of cache control remains the same as in V1, but the original name was very misleading as to how it operated.

V1's `IS_CHANGED` function signals execution not to trigger rerunning the node if the return value is the SAME as the last time the node was ran.

Thus, the function `IS_CHANGED` was renamed to `fingerprint_inputs`. One of the most common mistakes by developers was thinking if you return `True`, the node would always re-run. Because `True` would always be returned, it would have the opposite effect of only making the node run once and reuse cached values.

An example of using this function is the LoadImage node. It returns the hash of the selected file, so that if the file changes, the node will be forced to rerun.

**V1:**

```python  theme={null}
@classmethod
def IS_CHANGED(s, **kwargs):
    return "unique_value"
```

**V3:**

```python  theme={null}
@classmethod
def fingerprint_inputs(cls, **kwargs):
    return "unique_value"
```

### Step 6: Create Extension and Entry Point

Instead of defining dictionaries to link node id to node class/display name, there is now a `ComfyExtension` class and an expected `comfy_entrypoint` function to be defined.

In the future, more functions may be added to ComfyExtension to register more than just nodes via `get_node_list`.

`comfy_entrypoint` can be either async or not, but `get_node_list` must be defined as async.

**V1:**

```python  theme={null}
NODE_CLASS_MAPPINGS = {
    "Example": Example
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node"
}
```

**V3:**

```python  theme={null}
from comfy_api.latest import ComfyExtension

class MyExtension(ComfyExtension):
    # must be declared as async
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            Example,
            # Add more nodes here
        ]

# can be declared async or not, both will work
async def comfy_entrypoint() -> MyExtension:
    return MyExtension()
```

## Input Type Reference

Already explained in step 2, but here are some type reference comparisons in V1 vs V3. See `comfy_api.latest._io` for the full type declarations.

### Basic Types

| V1 Type     | V3 Type              | Example                                                      |
| ----------- | -------------------- | ------------------------------------------------------------ |
| `"INT"`     | `io.Int.Input()`     | `io.Int.Input("count", default=1, min=0, max=100)`           |
| `"FLOAT"`   | `io.Float.Input()`   | `io.Float.Input("strength", default=1.0, min=0.0, max=10.0)` |
| `"STRING"`  | `io.String.Input()`  | `io.String.Input("text", multiline=True)`                    |
| `"BOOLEAN"` | `io.Boolean.Input()` | `io.Boolean.Input("enabled", default=True)`                  |

#### control\_after\_generate

Int and Combo inputs support a `control_after_generate` parameter that adds a control widget for automatically changing the value after each generation. In V1 this was a plain `bool`; in V3 you can use the `io.ControlAfterGenerate` enum for explicit control. Passing `True` is equivalent to `io.ControlAfterGenerate.randomize`.

| Value                               | Behavior                                            |
| ----------------------------------- | --------------------------------------------------- |
| `io.ControlAfterGenerate.fixed`     | Value stays the same after each generation.         |
| `io.ControlAfterGenerate.increment` | Value increments by the step after each generation. |
| `io.ControlAfterGenerate.decrement` | Value decrements by the step after each generation. |
| `io.ControlAfterGenerate.randomize` | Value is randomized after each generation.          |

```python  theme={null}
# Enable the control widget (user picks the mode in the UI)
io.Int.Input("seed", default=0, min=0, max=0xFFFFFFFFFFFFFFFF, control_after_generate=True)

# Set a specific default mode
io.Int.Input("seed", default=0, min=0, max=0xFFFFFFFFFFFFFFFF,
    control_after_generate=io.ControlAfterGenerate.randomize)
```

### ComfyUI Types

| V1 Type          | V3 Type                   | Example                                          |
| ---------------- | ------------------------- | ------------------------------------------------ |
| `"IMAGE"`        | `io.Image.Input()`        | `io.Image.Input("image", tooltip="Input image")` |
| `"MASK"`         | `io.Mask.Input()`         | `io.Mask.Input("mask", optional=True)`           |
| `"LATENT"`       | `io.Latent.Input()`       | `io.Latent.Input("latent")`                      |
| `"CONDITIONING"` | `io.Conditioning.Input()` | `io.Conditioning.Input("positive")`              |
| `"MODEL"`        | `io.Model.Input()`        | `io.Model.Input("model")`                        |
| `"VAE"`          | `io.VAE.Input()`          | `io.VAE.Input("vae")`                            |
| `"CLIP"`         | `io.CLIP.Input()`         | `io.CLIP.Input("clip")`                          |

### Combo (Dropdowns/Selection Lists)

Combo types in V3 require explicit class definition.

**V1:**

```python  theme={null}
"mode": (["option1", "option2", "option3"],)
```

**V3:**

```python  theme={null}
io.Combo.Input("mode", options=["option1", "option2", "option3"])
```

## Schema Reference

The `Schema` dataclass defines all properties of a V3 node. Here is a complete reference of all available fields:

| Field               | Type           | Default    | Description                                                                                                         |
| ------------------- | -------------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| `node_id`           | `str`          | *required* | Globally unique ID of the node. Custom nodes should add a prefix/postfix to avoid clashes.                          |
| `display_name`      | `str`          | `None`     | Display name shown in the UI. Falls back to `node_id` if not set.                                                   |
| `category`          | `str`          | `"sd"`     | Category in the "Add Node" menu (e.g. `"image/transform"`).                                                         |
| `description`       | `str`          | `""`       | Tooltip shown when hovering over the node.                                                                          |
| `inputs`            | `list[Input]`  | `[]`       | List of input definitions.                                                                                          |
| `outputs`           | `list[Output]` | `[]`       | List of output definitions.                                                                                         |
| `hidden`            | `list[Hidden]` | `[]`       | List of hidden inputs to request (see [Hidden Inputs](#hidden-inputs)).                                             |
| `search_aliases`    | `list[str]`    | `[]`       | Alternative names for search. Useful for synonyms or old names after renaming.                                      |
| `is_output_node`    | `bool`         | `False`    | Marks the node as an output node, causing it and its dependencies to be executed.                                   |
| `is_input_list`     | `bool`         | `False`    | When True, all inputs become `list[type]` regardless of how many items are passed in.                               |
| `is_deprecated`     | `bool`         | `False`    | Flags the node as deprecated, signaling users to find alternatives.                                                 |
| `is_experimental`   | `bool`         | `False`    | Flags the node as experimental, warning users it may change.                                                        |
| `is_dev_only`       | `bool`         | `False`    | Hides the node from search/menus unless dev mode is enabled.                                                        |
| `is_api_node`       | `bool`         | `False`    | Flags the node as an API node for Comfy API services.                                                               |
| `not_idempotent`    | `bool`         | `False`    | When True, the node will always re-run and never reuse cached outputs from a different identical node in the graph. |
| `enable_expand`     | `bool`         | `False`    | Allows `NodeOutput` to include an `expand` property for node expansion.                                             |
| `accept_all_inputs` | `bool`         | `False`    | When True, all inputs from the prompt are passed as kwargs, even if not defined in the schema.                      |

### Common Input Parameters

All input types share these base parameters:

| Parameter      | Type   | Default    | Description                                                                       |
| -------------- | ------ | ---------- | --------------------------------------------------------------------------------- |
| `id`           | `str`  | *required* | Unique identifier for the input, used as the kwarg name in `execute`.             |
| `display_name` | `str`  | `None`     | Label shown in the UI. Defaults to `id`.                                          |
| `optional`     | `bool` | `False`    | Whether the input is optional.                                                    |
| `tooltip`      | `str`  | `None`     | Hover tooltip text.                                                               |
| `lazy`         | `bool` | `None`     | Marks input for lazy evaluation (see [Lazy Evaluation](#lazy-evaluation-v1--v3)). |
| `raw_link`     | `bool` | `None`     | When True, passes the raw link info instead of the resolved value.                |
| `advanced`     | `bool` | `None`     | When True, the input is hidden behind an "Advanced" toggle in the UI.             |

Widget inputs (Int, Float, String, Boolean, Combo) additionally support:

| Parameter     | Type   | Default | Description                                                               |
| ------------- | ------ | ------- | ------------------------------------------------------------------------- |
| `default`     | varies | `None`  | Default value for the widget.                                             |
| `socketless`  | `bool` | `None`  | When True, hides the input socket (widget only, no incoming connections). |
| `force_input` | `bool` | `None`  | When True, forces the widget to display as a socket input instead.        |

## Advanced Features

### Hidden Inputs

Hidden inputs provide access to execution context like the prompt metadata, node ID, and other internal values. They are not visible in the UI.

In V1, hidden inputs were declared as a `"hidden"` key in `INPUT_TYPES`. In V3, they are declared via the `hidden` parameter on the Schema, and their values are accessed via `cls.hidden`.

**V1:**

```python  theme={null}
@classmethod
def INPUT_TYPES(s):
    return {
        "required": {...},
        "hidden": {
            "unique_id": "UNIQUE_ID",
            "prompt": "PROMPT",
            "extra_pnginfo": "EXTRA_PNGINFO",
        }
    }

def execute(self, unique_id, prompt, extra_pnginfo, ...):
    # hidden values passed as regular arguments
    print(unique_id)
```

**V3:**

```python  theme={null}
@classmethod
def define_schema(cls) -> io.Schema:
    return io.Schema(
        node_id="MyNode",
        inputs=[...],
        hidden=[io.Hidden.unique_id, io.Hidden.prompt, io.Hidden.extra_pnginfo],
    )

@classmethod
def execute(cls, ...) -> io.NodeOutput:
    # hidden values accessed via cls.hidden
    print(cls.hidden.unique_id)
    print(cls.hidden.prompt)
    print(cls.hidden.extra_pnginfo)
```

Available hidden values:

| Hidden Enum                      | Description                                                            |
| -------------------------------- | ---------------------------------------------------------------------- |
| `io.Hidden.unique_id`            | The unique identifier of the node, matching the id on the client side. |
| `io.Hidden.prompt`               | The complete prompt sent by the client.                                |
| `io.Hidden.extra_pnginfo`        | Dictionary copied into metadata of saved `.png` files.                 |
| `io.Hidden.dynprompt`            | Instance of `DynamicPrompt` that may mutate during execution.          |
| `io.Hidden.auth_token_comfy_org` | Token acquired from signing into a ComfyOrg account on the frontend.   |
| `io.Hidden.api_key_comfy_org`    | API key generated by ComfyOrg, allows skipping frontend sign-in.       |

<Note>
  Some hidden values are automatically added based on Schema flags. Output nodes (`is_output_node=True`) automatically receive `prompt` and `extra_pnginfo`. API nodes (`is_api_node=True`) automatically receive auth tokens.
</Note>

### UI Helpers

V3 provides built-in UI helpers in the `ui` module to handle common patterns like previewing and saving files. Pass them to `io.NodeOutput` via the `ui` parameter.

#### Preview Helpers

Preview helpers save temporary files and return UI data for in-node display.

```python  theme={null}
from comfy_api.latest import ui

# Preview an image in the node
return io.NodeOutput(images, ui=ui.PreviewImage(images, cls=cls))

# Preview a mask (automatically converts to 3-channel for display)
return io.NodeOutput(mask, ui=ui.PreviewMask(mask, cls=cls))

# Preview audio
return io.NodeOutput(audio, ui=ui.PreviewAudio(audio, cls=cls))

# Preview text
return io.NodeOutput(ui=ui.PreviewText("Some text value"))

# Preview 3D model
return io.NodeOutput(ui=ui.PreviewUI3D(model_file, camera_info))
```

#### Save Helpers

Save helpers provide methods for saving files to the output directory with proper metadata embedding. They are typically used in output nodes.

```python  theme={null}
from comfy_api.latest import ui, io

# Save images and return UI data (most common pattern)
return io.NodeOutput(
    ui=ui.ImageSaveHelper.get_save_images_ui(
        images=images,
        filename_prefix=filename_prefix,
        cls=cls,  # passes hidden prompt/extra_pnginfo for metadata
    )
)

# Save animated PNG
return io.NodeOutput(
    ui=ui.ImageSaveHelper.get_save_animated_png_ui(
        images=images,
        filename_prefix=filename_prefix,
        cls=cls,
        fps=6.0,
        compress_level=4,
    )
)

# Save animated WebP
return io.NodeOutput(
    ui=ui.ImageSaveHelper.get_save_animated_webp_ui(
        images=images,
        filename_prefix=filename_prefix,
        cls=cls,
        fps=6.0,
        lossless=True,
        quality=80,
        method=4,
    )
)

# Save audio (supports flac, mp3, opus)
return io.NodeOutput(
    ui=ui.AudioSaveHelper.get_save_audio_ui(
        audio=audio,
        filename_prefix=filename_prefix,
        cls=cls,
        format="flac",
    )
)
```

<Tip>
  Passing `cls=cls` to save/preview helpers allows them to automatically embed workflow metadata (prompt, extra\_pnginfo) in the saved files. Make sure to include `io.Hidden.prompt` and `io.Hidden.extra_pnginfo` in your schema's hidden list, or set `is_output_node=True` which adds them automatically.
</Tip>

#### Returning Raw UI Dicts

If you need to return UI data that doesn't have a helper, you can pass a dict directly:

```python  theme={null}
return io.NodeOutput(ui={"images": results})
```

### Output Nodes

For nodes that produce side effects (like saving files). Same as in V1, marking a node as output will display a `run` play button in the node's context window, allowing for partial execution of the graph.

```python  theme={null}
@classmethod
def define_schema(cls) -> io.Schema:
    return io.Schema(
        node_id="SaveNode",
        inputs=[...],
        outputs=[],  # Does not need to be empty.
        is_output_node=True  # Mark as output node
    )
```

### Custom Types

Create custom input/output types either via class definition or the `Custom` helper function.

```python  theme={null}
from comfy_api.latest import io

# Method 1: Using decorator with class
@io.comfytype(io_type="MY_CUSTOM_TYPE")
class MyCustomType:
    Type = torch.Tensor  # Python type hint

    class Input(io.Input):
        def __init__(self, id: str, **kwargs):
            super().__init__(id, **kwargs)

    class Output(io.Output):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

# Method 2: Using Custom helper
# The helper can be used directly without saving to a variable first for convenience as well
MyCustomType = io.Custom("MY_CUSTOM_TYPE")
```

### MultiType Inputs

`MultiType` allows an input to accept more than one type. This is useful when a node can operate on different data types through the same input slot.

If the first argument (`id`) is an instance of an `Input` class instead of a string, that input will be used to create a widget with its overridden values. Otherwise, the input is socket-only.

```python  theme={null}
# Socket-only multi-type input (no widget)
io.MultiType.Input("input", types=[io.Image, io.Mask])

# Multi-type input with a widget fallback (String widget shown when nothing is connected)
io.MultiType.Input(
    io.String.Input("model_file", default="", multiline=False),
    types=[io.File3DGLB, io.File3DGLTF, io.File3DOBJ],
    tooltip="3D model file or path string",
)
```

### MatchType (Generic Type Matching)

`MatchType` creates type-linked inputs and outputs. When a user connects a specific type to a MatchType input, all other inputs and outputs sharing the same template automatically constrain to that type. This is how nodes like Switch and Create List work with any type.

```python  theme={null}
@classmethod
def define_schema(cls):
    # Create a template - all inputs/outputs sharing the same template will match types
    template = io.MatchType.Template("switch")
    return io.Schema(
        node_id="SwitchNode",
        display_name="Switch",
        category="logic",
        inputs=[
            io.Boolean.Input("switch"),
            io.MatchType.Input("on_false", template=template, lazy=True),
            io.MatchType.Input("on_true", template=template, lazy=True),
        ],
        outputs=[
            io.MatchType.Output(template=template, display_name="output"),
        ],
    )
```

You can also restrict which types are allowed:

```python  theme={null}
# Only allow Image, Mask, or Latent types
template = io.MatchType.Template("input_type", allowed_types=[io.Image, io.Mask, io.Latent])
```

### Dynamic Inputs

V3 introduces dynamic input types that change the available inputs based on user interaction. There is no V1 equivalent for these features.

#### Autogrow

`Autogrow` creates a variable number of inputs that automatically grow as the user connects more. There are two template types:

**TemplatePrefix** generates inputs with a numbered prefix (e.g. `image0`, `image1`, `image2`...):

```python  theme={null}
@classmethod
def define_schema(cls):
    autogrow_template = io.Autogrow.TemplatePrefix(
        input=io.Image.Input("image"),  # template for each input
        prefix="image",                  # prefix for generated input names
        min=2,                           # minimum number of inputs shown
        max=50,                          # maximum number of inputs allowed
    )
    return io.Schema(
        node_id="BatchImagesNode",
        display_name="Batch Images",
        category="image",
        inputs=[io.Autogrow.Input("images", template=autogrow_template)],
        outputs=[io.Image.Output()],
    )

@classmethod
def execute(cls, images: io.Autogrow.Type) -> io.NodeOutput:
    # 'images' is a dict mapping input names to their values
    image_list = list(images.values())
    return io.NodeOutput(batch(image_list))
```

**TemplateNames** generates inputs with specific names:

```python  theme={null}
template = io.Autogrow.TemplateNames(
    input=io.Float.Input("float"),
    names=["x", "y", "z"],  # explicit names for each input
    min=1,                    # minimum number of inputs shown
)
```

Autogrow can be combined with MatchType to create lists of type-matched inputs:

```python  theme={null}
@classmethod
def define_schema(cls):
    template_matchtype = io.MatchType.Template("type")
    template_autogrow = io.Autogrow.TemplatePrefix(
        input=io.MatchType.Input("input", template=template_matchtype),
        prefix="input",
    )
    return io.Schema(
        node_id="CreateList",
        display_name="Create List",
        category="logic",
        is_input_list=True,
        inputs=[io.Autogrow.Input("inputs", template=template_autogrow)],
        outputs=[
            io.MatchType.Output(
                template=template_matchtype,
                is_output_list=True,
                display_name="list",
            ),
        ],
    )
```

#### DynamicCombo

`DynamicCombo` creates a dropdown that shows/hides different inputs depending on the selected option. This is useful for nodes where different modes require different parameters.

```python  theme={null}
@classmethod
def define_schema(cls):
    return io.Schema(
        node_id="ResizeNode",
        display_name="Resize",
        category="transform",
        inputs=[
            io.Image.Input("image"),
            io.DynamicCombo.Input("resize_type", options=[
                io.DynamicCombo.Option("scale by dimensions", [
                    io.Int.Input("width", default=512, min=0, max=8192),
                    io.Int.Input("height", default=512, min=0, max=8192),
                ]),
                io.DynamicCombo.Option("scale by multiplier", [
                    io.Float.Input("multiplier", default=1.0, min=0.01, max=8.0),
                ]),
                io.DynamicCombo.Option("scale to megapixels", [
                    io.Float.Input("megapixels", default=1.0, min=0.01, max=16.0),
                ]),
            ]),
        ],
        outputs=[io.Image.Output()],
    )

@classmethod
def execute(cls, image, resize_type: dict) -> io.NodeOutput:
    # resize_type is a dict containing the selected option key and its inputs
    selected = resize_type["resize_type"]
    if selected == "scale by dimensions":
        width = resize_type["width"]
        height = resize_type["height"]
        # ...
    elif selected == "scale by multiplier":
        multiplier = resize_type["multiplier"]
        # ...
```

DynamicCombo options can also be nested:

```python  theme={null}
io.DynamicCombo.Input("combo", options=[
    io.DynamicCombo.Option("option1", [io.String.Input("string")]),
    io.DynamicCombo.Option("option2", [
        io.DynamicCombo.Input("subcombo", options=[
            io.DynamicCombo.Option("sub_opt1", [io.Float.Input("x"), io.Float.Input("y")]),
            io.DynamicCombo.Option("sub_opt2", [io.Mask.Input("mask", optional=True)]),
        ])
    ]),
])
```

### Async Execute

V3 supports async `execute` methods. This is useful for nodes that perform I/O operations, API calls, or other async work. Simply declare `execute` as `async`:

```python  theme={null}
@classmethod
async def execute(cls, prompt, **kwargs) -> io.NodeOutput:
    result = await some_async_operation(prompt)
    return io.NodeOutput(result)
```

### ComfyAPI

The `ComfyAPI` class provides access to ComfyUI runtime services like progress reporting and node replacement registration. Import it and create an instance:

```python  theme={null}
from comfy_api.latest import ComfyAPI

api = ComfyAPI()
```

#### Progress Reporting

Report execution progress from within a node's `execute` method. The progress bar is displayed in the ComfyUI interface. This replaces the V1 pattern of using `comfy.utils.PROGRESS_BAR_HOOK`.

```python  theme={null}
from comfy_api.latest import ComfyAPI

api = ComfyAPI()

@classmethod
async def execute(cls, images, **kwargs) -> io.NodeOutput:
    total = len(images)
    for i, image in enumerate(images):
        process(image)
        await api.execution.set_progress(
            value=i + 1,
            max_value=total,
            preview_image=image,  # optional: show preview during progress
        )
    return io.NodeOutput(result)
```

<Note>
  `set_progress` can accept a PIL Image, an `ImageInput` tensor, or `None` for the `preview_image` parameter. When called from within `execute`, the `node_id` is automatically determined from the executing context.
</Note>

#### Node Replacement

Node replacement allows mapping old/deprecated nodes to new ones, so existing workflows automatically upgrade. Register replacements using the `ComfyAPI` in your extension's `on_load` method.

```python  theme={null}
from comfy_api.latest import ComfyAPI, ComfyExtension, io

api = ComfyAPI()

class MyExtension(ComfyExtension):
    async def on_load(self) -> None:
        await api.node_replacement.register(io.NodeReplace(
            new_node_id="MyNewNode",
            old_node_id="MyOldNode",
            old_widget_ids=["param1", "param2"],  # ordered widget IDs for positional mapping
            input_mapping=[
                {"new_id": "image", "old_id": "input_image"},       # rename input
                {"new_id": "method", "set_value": "lanczos"},       # set a fixed value
            ],
            output_mapping=[
                {"new_idx": 0, "old_idx": 0},  # map output by index
            ],
        ))

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [MyNewNode]
```

The `old_widget_ids` parameter is important: workflow JSON stores widget values by position index, not by name. This list maps those positional indexes to input IDs so the replacement system can correctly identify widget values during migration.

For nodes using dynamic inputs (like Autogrow), use dotted paths in the mapping:

```python  theme={null}
input_mapping=[
    {"new_id": "images.image0", "old_id": "image1"},
    {"new_id": "images.image1", "old_id": "image2"},
]
```

### Extension Lifecycle

The `ComfyExtension` class supports lifecycle hooks beyond just `get_node_list`:

```python  theme={null}
from comfy_api.latest import ComfyExtension, io

class MyExtension(ComfyExtension):
    async def on_load(self) -> None:
        """Called when the extension is loaded.
        Use for one-time initialization: registering node replacements,
        setting up global resources, etc.
        """
        pass

    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the list of node classes this extension provides."""
        return [MyNode]

async def comfy_entrypoint() -> MyExtension:
    return MyExtension()
```

### NodeOutput

The `NodeOutput` class is the standardized return value from `execute`. It supports several patterns:

```python  theme={null}
# Return a single output value
return io.NodeOutput(image)

# Return multiple output values (order matches outputs list in schema)
return io.NodeOutput(width, height, batch_size)

# Return only UI data (no output values)
return io.NodeOutput(ui=ui.PreviewImage(images, cls=cls))

# Return both output values and UI data
return io.NodeOutput(image, ui=ui.PreviewImage(image, cls=cls))

# Return None/empty (for nodes with no outputs)
return io.NodeOutput()
```

## Complete Example

Here is a complete example of a V3 extension file with multiple nodes:

```python  theme={null}
from comfy_api.latest import ComfyExtension, io, ui

class InvertImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyPack_InvertImage",  # prefixed to avoid clashes
            display_name="Invert Image",
            category="my_pack/image",
            description="Inverts the colors of an image.",
            inputs=[
                io.Image.Input("image"),
            ],
            outputs=[
                io.Image.Output(display_name="inverted"),
            ],
        )

    @classmethod
    def execute(cls, image) -> io.NodeOutput:
        inverted = 1.0 - image
        return io.NodeOutput(inverted, ui=ui.PreviewImage(inverted, cls=cls))


class SaveImage(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MyPack_SaveImage",
            display_name="Save Image",
            category="my_pack/image",
            is_output_node=True,
            inputs=[
                io.Image.Input("images"),
                io.String.Input("filename_prefix", default="ComfyUI"),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, images, filename_prefix) -> io.NodeOutput:
        return io.NodeOutput(
            ui=ui.ImageSaveHelper.get_save_images_ui(
                images=images,
                filename_prefix=filename_prefix,
                cls=cls,
            )
        )


class MyPackExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [InvertImage, SaveImage]

async def comfy_entrypoint() -> MyPackExtension:
    return MyPackExtension()
```





# Add node docs for your ComfyUI custom node

> How to create rich documentation for your custom nodes

## Node Documentation with Markdown

Custom nodes can include rich markdown documentation that will be displayed in the UI instead of the generic node description. This provides users with detailed information about your node's functionality, parameters, and usage examples.

If you have already added tooltips for each parameter in the node definition, this basic information can be directly accessed via the node documentation panel.
No additional node documentation needs to be added, and you can refer to the related implementation of [ContextWindowsManualNode](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_context_windows.py#L7)

## Setup

To add documentation for your custom nodes or multi-language support documentation:

1. Create a `docs` folder inside your `WEB_DIRECTORY`
2. Add markdown files named after your nodes (the names of your nodes are the dictionary keys in the `NODE_CLASS_MAPPINGS` dictionary used to register the nodes):
   * `WEB_DIRECTORY/docs/NodeName.md` - Default documentation
   * `WEB_DIRECTORY/docs/NodeName/en.md` - English documentation
   * `WEB_DIRECTORY/docs/NodeName/zh.md` - Chinese documentation
   * Add other locales as needed (e.g., `fr.md`, `de.md`, etc.)

The system will automatically load the appropriate documentation based on the user's locale, falling back to `NodeName.md` if a localized version is not available.

## Supported Markdown Features

* Standard markdown syntax (headings, lists, code blocks, etc.)
* Images using markdown syntax: `![alt text](image.png)`
* HTML media elements with specific attributes:
  * `<video>` and `<source>` tags
  * Allowed attributes: `controls`, `autoplay`, `loop`, `muted`, `preload`, `poster`

## Example Structure

```
my-custom-node/
├── __init__.py
├── web/              # WEB_DIRECTORY
│   ├── js/
│   │   └── my-node.js
│   └── docs/
│       ├── MyNode.md           # Fallback documentation
│       └── MyNode/
│           ├── en.md           # English version
│           └── zh.md           # Chinese version
```

## Example Markdown File

```markdown  theme={null}
# My Custom Node

This node processes images using advanced algorithms.

## Parameters

- **image**: Input image to process
- **strength**: Processing strength (0.0 - 1.0)

## Usage

![example usage](example.png)

<video controls loop muted>
  <source src="demo.mp4" type="video/mp4">
</video>
```



# Workflow templates

If you have example workflow files associated with your custom nodes
then ComfyUI can show these to the user in the template browser (`Workflow`/`Browse Templates` menu).
Workflow templates are a great way to support people getting started with your nodes.

All you have to do as a node developer is to create an `example_workflows` folder and place the `json` files there.
Optionally you can place `jpg` files with the same name to be shown as the template thumbnail.

Under the hood ComfyUI statically serves these files along with an endpoint (`/api/workflow_templates`)
that returns the collection of workflow templates.

<Note>
  The following folder names are also accepted, but we still recommend using `example_workflows`

  * workflow
  * workflows
  * example
  * examples
</Note>

## Example

Under `ComfyUI-MyCustomNodeModule/example_workflows/` directory:

* `My_example_workflow_1.json`
* `My_example_workflow_1.jpg`
* `My_example_workflow_2.json`

In this example ComfyUI's template browser shows a category called `ComfyUI-MyCustomNodeModule` with two items, one of which has a thumbnail.

For a real-world example, see [ComfyUI-Impact-Pack's example\_workflows folder](https://github.com/ltdrdata/ComfyUI-Impact-Pack/tree/Main/example_workflows).





# Subgraph blueprints

If you have reusable subgraph components associated with your custom nodes, ComfyUI can make these available to users as global subgraph blueprints. Subgraph blueprints allow users to quickly add pre-built node groups from the subgraph menu.

All you have to do as a node developer is create a `subgraphs` folder in your custom node directory and place the `.json` files there.

Under the hood, ComfyUI scans all custom node directories for subgraph files and serves them via the `/global_subgraphs` API endpoint.

## Example

Under `ComfyUI-MyCustomNodeModule/subgraphs/` directory:

* `My_upscale_subgraph.json`
* `My_effects_subgraph.json`

In this example, ComfyUI's subgraph browser shows blueprints from `ComfyUI-MyCustomNodeModule` that users can add to their workflows.

## Creating a subgraph JSON file

Subgraph JSON files use the same format as workflow JSON files. The easiest way to create one:

1. Build your subgraph in ComfyUI
2. Select the nodes you want to include
3. Convert them to a subgraph
4. Export the subgraph as JSON
5. Place the JSON file in your `subgraphs/` folder

## See also

* [Subgraphs (User Guide)](/interface/features/subgraph) - How users interact with subgraphs
* [Subgraph Developer Guide](/custom-nodes/js/subgraphs) - Frontend extension development for subgraphs
* [Workflow templates](/custom-nodes/workflow_templates) - Adding example workflows to your custom nodes







# Node Definition JSON

> JSON schema for a ComfyUI Node.

The node definition JSON is defined using [JSON Schema](https://json-schema.org/). Changes to this schema will be discussed in the [rfcs repo](https://github.com/comfy-org/rfcs).

## v2.0 (Latest)

```json Node Definition v2.0 theme={null}
{
  "$ref": "#/definitions/ComfyNodeDefV2",
  "definitions": {
    "ComfyNodeDefV2": {
      "type": "object",
      "properties": {
        "inputs": {
          "type": "object",
          "additionalProperties": {
            "anyOf": [
              {
                "type": "object",
                "properties": {
                  "default": {
                    "anyOf": [
                      {
                        "type": "number"
                      },
                      {
                        "type": "array",
                        "items": {
                          "type": "number"
                        }
                      }
                    ]
                  },
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "min": {
                    "type": "number"
                  },
                  "max": {
                    "type": "number"
                  },
                  "step": {
                    "type": "number"
                  },
                  "display": {
                    "type": "string",
                    "enum": [
                      "slider",
                      "number",
                      "knob"
                    ]
                  },
                  "control_after_generate": {
                    "type": "boolean"
                  },
                  "type": {
                    "type": "string",
                    "const": "INT"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              },
              {
                "type": "object",
                "properties": {
                  "default": {
                    "anyOf": [
                      {
                        "type": "number"
                      },
                      {
                        "type": "array",
                        "items": {
                          "type": "number"
                        }
                      }
                    ]
                  },
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "min": {
                    "type": "number"
                  },
                  "max": {
                    "type": "number"
                  },
                  "step": {
                    "type": "number"
                  },
                  "display": {
                    "type": "string",
                    "enum": [
                      "slider",
                      "number",
                      "knob"
                    ]
                  },
                  "round": {
                    "anyOf": [
                      {
                        "type": "number"
                      },
                      {
                        "type": "boolean",
                        "const": false
                      }
                    ]
                  },
                  "type": {
                    "type": "string",
                    "const": "FLOAT"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              },
              {
                "type": "object",
                "properties": {
                  "default": {
                    "type": "boolean"
                  },
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "label_on": {
                    "type": "string"
                  },
                  "label_off": {
                    "type": "string"
                  },
                  "type": {
                    "type": "string",
                    "const": "BOOLEAN"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              },
              {
                "type": "object",
                "properties": {
                  "default": {
                    "type": "string"
                  },
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "multiline": {
                    "type": "boolean"
                  },
                  "dynamicPrompts": {
                    "type": "boolean"
                  },
                  "defaultVal": {
                    "type": "string"
                  },
                  "placeholder": {
                    "type": "string"
                  },
                  "type": {
                    "type": "string",
                    "const": "STRING"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              },
              {
                "type": "object",
                "properties": {
                  "default": {},
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "control_after_generate": {
                    "type": "boolean"
                  },
                  "image_upload": {
                    "type": "boolean"
                  },
                  "image_folder": {
                    "type": "string",
                    "enum": [
                      "input",
                      "output",
                      "temp"
                    ]
                  },
                  "allow_batch": {
                    "type": "boolean"
                  },
                  "video_upload": {
                    "type": "boolean"
                  },
                  "remote": {
                    "type": "object",
                    "properties": {
                      "route": {
                        "anyOf": [
                          {
                            "type": "string",
                            "format": "uri"
                          },
                          {
                            "type": "string",
                            "pattern": "^\\/"
                          }
                        ]
                      },
                      "refresh": {
                        "anyOf": [
                          {
                            "type": "number",
                            "minimum": -9007199254740991,
                            "maximum": 9007199254740991
                          },
                          {
                            "type": "number",
                            "maximum": 9007199254740991,
                            "minimum": -9007199254740991
                          }
                        ]
                      },
                      "response_key": {
                        "type": "string"
                      },
                      "query_params": {
                        "type": "object",
                        "additionalProperties": {
                          "type": "string"
                        }
                      },
                      "refresh_button": {
                        "type": "boolean"
                      },
                      "control_after_refresh": {
                        "type": "string",
                        "enum": [
                          "first",
                          "last"
                        ]
                      },
                      "timeout": {
                        "type": "number",
                        "minimum": 0
                      },
                      "max_retries": {
                        "type": "number",
                        "minimum": 0
                      }
                    },
                    "required": [
                      "route"
                    ],
                    "additionalProperties": false
                  },
                  "options": {
                    "type": "array",
                    "items": {
                      "type": [
                        "string",
                        "number"
                      ]
                    }
                  },
                  "type": {
                    "type": "string",
                    "const": "COMBO"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              },
              {
                "type": "object",
                "properties": {
                  "default": {},
                  "defaultInput": {
                    "type": "boolean"
                  },
                  "forceInput": {
                    "type": "boolean"
                  },
                  "tooltip": {
                    "type": "string"
                  },
                  "hidden": {
                    "type": "boolean"
                  },
                  "advanced": {
                    "type": "boolean"
                  },
                  "rawLink": {
                    "type": "boolean"
                  },
                  "lazy": {
                    "type": "boolean"
                  },
                  "type": {
                    "type": "string"
                  },
                  "name": {
                    "type": "string"
                  },
                  "isOptional": {
                    "type": "boolean"
                  }
                },
                "required": [
                  "type",
                  "name"
                ],
                "additionalProperties": true
              }
            ]
          }
        },
        "outputs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "index": {
                "type": "number"
              },
              "name": {
                "type": "string"
              },
              "type": {
                "type": "string"
              },
              "is_list": {
                "type": "boolean"
              },
              "options": {
                "type": "array"
              },
              "tooltip": {
                "type": "string"
              }
            },
            "required": [
              "index",
              "name",
              "type",
              "is_list"
            ],
            "additionalProperties": false
          }
        },
        "hidden": {
          "type": "object",
          "additionalProperties": {}
        },
        "name": {
          "type": "string"
        },
        "display_name": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "category": {
          "type": "string"
        },
        "output_node": {
          "type": "boolean"
        },
        "python_module": {
          "type": "string"
        },
        "deprecated": {
          "type": "boolean"
        },
        "experimental": {
          "type": "boolean"
        }
      },
      "required": [
        "inputs",
        "outputs",
        "name",
        "display_name",
        "description",
        "category",
        "output_node",
        "python_module"
      ],
      "additionalProperties": false
    }
  },
  "$schema": "http://json-schema.org/draft-07/schema#"
}
```






