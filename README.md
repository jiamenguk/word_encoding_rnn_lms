# Setup

Install OpenFST and its Python extension following instructions at [OpenFST](http://www.openfst.org/twiki/bin/view/FST/PythonExtension "OpenFST")

Install the required numpy and TensorFlow at using:

`pip install requirements.txt`

# Running encoding scripts

For each encoding scheme, there is a `read_file.py` which takes an input in the first system argument and spits out a mapping of the words in the input file to the decomposed subword units in a hash table. This is stored in JSON as a dict.

`python $SCHEME/read_file.py ../data/de/wmt15.de`

Note that for BPE this is done using the `learn_bpe.py` file

The `squash.py` takes in an input file and the dictionary mapping to output the encoded text.

This output file can then be used to train LM models

~~~
cd lm_train
python ptb_word_lm.py --data_path ../data/de/wmt15.de.$SCHEME --train_path ./$SCHEME/ 
~~~

This also outputs a file in IDs and the mapping of the words (`.ids` file) to the IDs in the `.wmap` file.

The `nbest_mapper.py` file in the encoding scripts take these `.wmap` files and the UCAM-SMT mapping files and creates a mapping from the UCAM word IDs to the subword IDs. The script then opens directories of N-Best outputs from the OpenFST lattice and converts them into the subword IDs. (This section may some times be commented out) (To be extended)

There may also be `FST_Conv.py` scripts which builds a mapping transducer, same to that described `nbest_mapper.py` and outputs transformed lattices.

# Rescoring

N-best rescoring is done by running 

~~~
cd lm_train
python ptb_word_lm.py --data_path $PATH_TO_MAPPED_NBEST_OUTPUTS --train_path ./$SCHEME/ --wmap_path ../data/de/wmt15.de.$SCHEME.wmap --outfile ./nbest-$SCHEME/
~~~