import pandas as pd
import plotly.express as px
from sklearn.metrics import precision_recall_curve, auc

predictions_file = "models/highlighter/sbert2.csv"

if __name__ == "__main__":
    # Load predictions and calculate Precision-Recall curve
    predictions = pd.read_csv(predictions_file)
    precision, recall, _ = precision_recall_curve(
        predictions["label"], predictions["score"]
    )
    fig = px.area(
        x=recall, y=precision,
        title=f'Precision-Recall Curve (AUC={auc(recall, precision):.4f})',
        labels = {
            "x": 'Recall',
            "y": 'Precision'
        },
        width=500, height=500
    )
    fig.update_layout(
        font=dict(
        size=18
    )
    )
    # Add reference line of random prediction
    random_pred_precision = predictions["label"].mean()
    fig.add_shape(
        type='line', line=dict(dash='dash'),
        x0=0, x1=1, y0=random_pred_precision, y1=random_pred_precision
    )
    # fig.update_yaxes(scaleanchor="x", scaleratio=1)
    # fig.update_xaxes(constrain='domain')
    fig.show()