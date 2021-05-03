from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import seaborn as sns
import pandas as pd
import wandb
import numpy as np
import matplotlib.pyplot as plt
import scprep
import phate


def visualize_embeddings_2D(embs, numeric_labels, tsne_perplexity, pca_k_n_comps=None, seed=100, verbose=0):
    df = pd.DataFrame()
    df["y"] = np.array(numeric_labels)

    # Data for plot 1
    pca = PCA(n_components=2, random_state=seed)
    pca_result = pca.fit_transform(embs)
    df['pca-1'] = pca_result[:, 0]
    df['pca-2'] = pca_result[:, 1]

    # Data for plot 2
    tsne = TSNE(n_components=2, verbose=verbose,
                perplexity=tsne_perplexity, n_iter=1000, random_state=seed)
    tsne_results = tsne.fit_transform(embs)
    df["tsne-1"] = tsne_results[:, 0]
    df["tsne-2"] = tsne_results[:, 1]

    # Actual plotting
    plt.figure(figsize=(24, 4))
    ax1 = plt.subplot(1, 3, 1)
    sns.scatterplot(
        x="pca-1", y="pca-2",
        hue=df.y.tolist(),
        palette="bright",
        data=df,
        legend=False,
        ax=ax1
    ).set(title="PCA projection")

    ax2 = plt.subplot(1, 3, 2)
    sns.scatterplot(
        x="tsne-1", y="tsne-2",
        hue=df.y.tolist(),
        palette="bright",
        data=df,
        legend=False if pca_k_n_comps else "auto",
        ax=ax2
    ).set(title="t-SNE projection")

    if pca_k_n_comps:
        # Data for plot 3
        pca_k = PCA(n_components=pca_k_n_comps, random_state=seed)
        pca_k_result = pca_k.fit_transform(embs)
        tsne = TSNE(n_components=2, verbose=1,
                    perplexity=tsne_perplexity, n_iter=1000, random_state=seed)
        tsne_pca_results = tsne.fit_transform(pca_k_result)
        df[f"tsne-pca-{pca_k_n_comps}-1"] = tsne_pca_results[:, 0]
        df[f"tsne-pca-{pca_k_n_comps}-2"] = tsne_pca_results[:, 1]

        # Actual plotting
        ax3 = plt.subplot(1, 3, 3)
        sns.scatterplot(
            x=f"tsne-pca-{pca_k_n_comps}-1", y=f"tsne-pca-{pca_k_n_comps}-2",
            hue=df.y.tolist(),
            palette="bright",
            data=df,
            ax=ax3
        ).set(title="t-SNE on PCA projection")

    plt.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)

    # wandb code
    fig = plt.gcf()
    fig.set_size_inches(15, 10)  # enlarging embeddings
    wandb.log({"PCA_2D_embedding": wandb.Image(fig)})
    plt.close()  # to prevent plotting at testing time


def visualize_PCA_embeddings_3D(embs, labels, fname=None, seed=100):
    pca = PCA(n_components=3, random_state=seed)
    pca_result = pca.fit_transform(embs)
    data = np.vstack([pca_result[:, 0], pca_result[:, 1], pca_result[:, 2]]).T
    colors = np.array(labels)

    return scprep.plot.rotate_scatter3d(data, c=colors, figsize=(10, 8), title=f"PCA 3 components",
                                        legend_anchor=(1.01, 1), filename=fname)


def visualize_tSNE_embeddings_3D(embs, labels, perplexity=50, fname=None, seed=100):
    tsne = TSNE(n_components=3, verbose=1, perplexity=perplexity,
                n_iter=1000, random_state=seed)
    tsne_result = tsne.fit_transform(embs)
    data = np.vstack(
        [tsne_result[:, 0], tsne_result[:, 1], tsne_result[:, 2]]).T
    colors = np.array(labels)

    return scprep.plot.rotate_scatter3d(data, c=colors, figsize=(10, 8), title=f"t-SNE {perplexity} perplexity",
                                        legend_anchor=(1.01, 1), filename=fname)


def visualize_phate_embeddings_2D(embs, labels, knn=4, decay=15, t=12, seed=100):
    phate_operator = phate.PHATE(knn=knn, decay=decay,
                                 t=t, random_state=seed)  # (k=2, t=5000, n_pca=50, random_state=69420, knn_dist='cosine')
    tree_phate = phate_operator.fit_transform(embs)
    return phate.plot.scatter2d(phate_operator, c=labels, legend_anchor=(1.01, 1))


def visualize_phate_embeddings_3D(embs, labels, knn=4, decay=15, t=12, seed=100, fname=None):
    phate_operator = phate.PHATE(knn=knn, decay=decay,
                                 t=t, random_state=seed)  # (k=2, t=5000, n_pca=50, random_state=69420, knn_dist='cosine')
    tree_phate = phate_operator.fit_transform(embs)
    return phate.plot.rotate_scatter3d(phate_operator, c=labels, legend_anchor=(1.01, 1),
                                       filename=fname)
