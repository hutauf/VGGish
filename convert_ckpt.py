'''



'''

def convert():
    import tensorflow as tf
    import tensorflow.keras.backend as K
    import openmic.vggish as ovg
    import openmic.vggish.slim

    sess = K.get_session()

    # build full old model
    with tf.name_scope('slim'):
        ovg.slim.define_vggish_slim(training=False)
        ovg.slim.load_vggish_slim_checkpoint(sess, ovg.params.MODEL_PARAMS)
        vggish_vars = [v for v in tf.global_variables()]

        # get old var name -> tensor value
        old_vars = {
            v.name: x for v, x in zip(vggish_vars, sess.run(vggish_vars))
        }

    import vggish_keras as vgk

    # build full new model
    model = vgk.VGGish(vgk.get_pump(), include_top=True, compress=True, weights=None)

    # get new var name -> new var
    new_vars = {
        v.name: v for v in set(model.trainable_weights) | set(model.non_trainable_weights)
    }

    # set weights for network
    for old_v in old_vars:
        new_v = (
            old_v.replace('weights:0', 'kernel:0')
                 .replace('biases:0', 'bias:0'))

        print(old_v, new_v, new_v in new_vars)
        print(old_vars[old_v].shape, new_vars[new_v])
        print()

        new_vars[new_v].assign(old_vars[old_v])

    # set post processing weights
    model.layers[-1].set_weights([
        ovg.__pproc__._pca_matrix,
        ovg.__pproc__._pca_means])

    model.summary()

    model.save('vggish_audioset_weights.h5')

if __name__ == '__main__':
    convert()
