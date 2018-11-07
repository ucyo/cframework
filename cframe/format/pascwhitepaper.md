# Pascal (PSC) File Format

This documentation should help define the Pasc file format.

## Format

The File has following format:

```
PSC    = HEADER DATA
HEADER = MAGIC NDIM DIMLEN NVARS
MAGIC  = 'PSC0' | 'PSC1'
NDIM   = UINT8
DIMLEN = [UINT32..]
NVARS  = UINT8

DATA      = [STREAM..]
STREAM    = PADFLAG INFOFLAG (START)? BLZCLEN BNOISELEN BLZC BNOISE
FLAG      = UINT8
START     = UINT32
BLZCLEN   = UINT32
BNOISELEN = UINT32
BLZC      = [UINT8..]
BNOISE    = [UINT8..]
```

### Details

The **HEADER** includes the magic bytes, the shape and number of array(s).

    **Note** The format assumes that each array in the data block has the same shape as given in the header.   

- **MAGIC** [4 Byte] is either 'PSC0' or 'PSC1'. The 'PSC1' magic code is a placeholder for the next iteration of this format.
- **NDIM** [4 Byte] number of dimensions of the arrays.
- **DIMLEN** [4 Byte ..] size of each dimension of the array.
- **NVARS** [4 Byte] number of arrays in the data block.

The **DATA** block consists of several **STREAM**. The number of streams is given in **NVARS**.

- **PADFLAG** [1 Byte] consists of padding information.
  - [0-3] Number of padded bits in **BNOISE** to make it byte length.
  - [5-7] Number of padded bits in **BLZC** to make it byte length.
- **INFOFLAG** [1 Byte] consists of information about the dataset.
  - [0-4] Empty Placeholder
  - [5] Endianess of dataset.
  - [6] Information about the startvalue. True if startvalue is 0 and False otherwise.
  - [7] Information about the datatype. True if datatype is float and False if it is a double.
- **START** [4 Byte] is the startvalue of the traversal. It only exists if the startvalue in **FLAG** is False.
- **BLZCLEN** [4 Byte] gives information about how long the compressed LZC block in binary is.
- **BNOISELEN** [4 Byte] gives information about how long the compressed Resiude block in binary is.
- **BLZC** [1 Byte ..] binary compressed LZC block.
- **BNOISE** [1 Byte ..] binary compressed Residue block.
