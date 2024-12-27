# Mine Real Speech from ASR Dataset

Currently, we try to mine from VoxPopuli German data.

## Slot Filling
### 1. Extract all slots

We find all the phrases and labels from annotated data in MASSIVE.
We now expect each phrase has a single label.

Something to consider: do we need information about train/test/dev?

### 2. Search for the slots

Currently, this is not working very well, because the annotations are ambiguous sometimes.

## Intent
This is based on text mining.

### 1. Prepare meta data
Extract sentences and number of lines from datasets.

```
qsub entries/make_data.sh
```

### 2. Embed sentences

Apply LASER2 to the extracted sentences.
```
qsub entries/embed_text.sh
```

### 3. Train indices

I don't need to train an index for MASSIVE, just FLAT.
But I need an index for CommonVoice.
```
qsub entries/train_index.sh
```

### 4. Apply mining

Currently, the text files are only the transcriptions.
In the future, I think that should contain audio info.
```
qsub entries/text_mining.sh
```
