//Jamal 28/03
import javafx.animation.AnimationTimer;
import javafx.application.*;
import javafx.event.EventHandler;
import javafx.scene.*;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.KeyEvent;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Rectangle;
import javafx.stage.Stage;
import javafx.geometry.*;

public class View extends Application{

	public static final int SCREEN_WIDTH = 1024;
	public static final int SCREEN_HEIGHT = 768;
	
	private Game game;
	
	public static void main(String[] args) {
		launch(args);
	}
	
	public void start(Stage stage){
		
		//Set up a container and a group to hold all the elements to display to the user
		Group root = new Group();
		Scene scene = new Scene(root);
		
		//Set up properties of the window that displays the game to the user
		stage.setTitle("MOONBALLERS");
		stage.setScene(scene);
		stage.setWidth(SCREEN_WIDTH);
		stage.setHeight(SCREEN_HEIGHT);
		stage.setResizable(false);
		
		Canvas canvas = new Canvas(SCREEN_HEIGHT,SCREEN_WIDTH);
		root.getChildren().add(canvas);
		GraphicsContext gc = canvas.getGraphicsContext2D();
		stage.show();
		
		game = new Game(root); //create a game using the constructor that allows GUI to be displayed to user
		
		AnimationTimer timer = new AnimationTimer() {
            @Override
            public void handle(long now) {
                game.tick(); //causes game to progress by in-built tick frequency of 60 frames per second
                if (game.goPaddleLeft == true) { //Checks condition in controller class and sends message to controller class to update paddle model
                	game.movePaddleLeft();
                }
                else if (game.goPaddleRight == true) {
                	game.movePaddleRight();
                }
            }
        };
        
        timer.start();
        
        //keyboard input handling, sets variables in game control class so that paddle model classes can behave accordingly
        scene.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent event) {
                switch (event.getCode()) {
                    case LEFT:  game.goPaddleLeft = true; break;
                    case RIGHT:  game.goPaddleRight = true; break;
                }
            }
        });
        
        scene.setOnKeyReleased(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent event) {
                switch (event.getCode()) {
                    case LEFT:  game.goPaddleLeft = false; break;
                    case RIGHT: game.goPaddleRight = false; break;
                }
            }
        });
      
        //update the view that the user sees after keyboard input handling takes place.
        stage.setScene(scene);
        stage.show();
	}
}
