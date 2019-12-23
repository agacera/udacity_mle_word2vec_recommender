from pathlib import Path
import word2vec_recommender.explorer as exp

app = exp.create_dash_app(dataset_path=Path("./data/ml-latest-small/"), model_path=Path("./data/best_model"))
app.run_server(debug=False, port=9898, host='0.0.0.0')