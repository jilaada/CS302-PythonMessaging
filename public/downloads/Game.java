
//Jamal 28/03
import javafx.scene.shape.*;
import javafx.scene.Group;
import javafx.scene.canvas.Canvas;
import javafx.scene.paint.Color;

public class Game implements IGame {
	
	//Declare member variables of this control class
	public static final int SCREEN_WIDTH = 1024;
	public static final int SCREEN_HEIGHT = 768;
	private Paddle paddle;
	private Ball ball;
	private Group root;
	private Canvas canvas;
	private Wall wall;
	private Waaalll p1Wall;
	private Warlord warlord1;
	private Warlord warlord2;
	private int numberWarlords;
	boolean finished = false;
	boolean goPaddleLeft;
	boolean goPaddleRight;
	int time = 180;
	/***
     * A tick advances the state of the game world by a small time increment, i.e. one frame. The ball (and all other
     *  objects) should move according to their velocity, player inputs should be handled (but are not tested here),
     *  collisions should be detected and processed, game end conditions should be checked, and so on.
     */
	
	//Constructor for the control class with no inputs, to initialise control class variables for testing
	Game(){
		root = new Group();
		canvas = new Canvas(SCREEN_WIDTH,SCREEN_HEIGHT);
		ball = new Ball();
		wall = new Wall();
		paddle = new Paddle();
		numberWarlords = 2;
		warlord1 = new Warlord();
		warlord2 = new Warlord();
	}
	
	//Constructor that takes in a Group class as an input, so that variables can be initialised
	//and objects can be displayed on a GUI
	Game(Group root){
		this.root = root;
		ball = new Ball(50,300,5,root);
		wall = new Wall(200,150,root);
		paddle = new Paddle(100, 10, 120, 300, root);
		warlord1 = new Warlord(60,60,20,root);
		warlord2 = new Warlord();
		p1Wall = new Waaalll(root);
	}
	
	void checkWindowBoundaryCollision(){
		//if current position of the ball plus the distance that it wants to move is greater than the height or width  of the screen,
    	//or if the current position of the ball plus the distance that it wants to move is less than 0 the other side of the screen,
    	//set the velocity of the ball to the opposite direction
		if(ball.getXPos()+ball.getXVelocity()>(SCREEN_WIDTH-ball.getRadius())|| ball.getXPos()+ball.getXVelocity()<0){
			ball.setXVelocity(-1*ball.getXVelocity());
		}
		if(ball.getYPos()+ball.getYVelocity()>(SCREEN_HEIGHT-ball.getRadius())|| ball.getYPos()+ball.getYVelocity()<0){
			ball.setYVelocity(-1*ball.getYVelocity());
		}
	}
	
	void checkWallCollision(){
		if(ball.getNode().intersects(wall.getBounds())){ //Ball touches wall somewhere
			if(!wall.isDestroyed()){ //mark the wall as destroyed if the ball intersects it and unassign it from the warlord
				wall.destroy();
				warlord1.removeWall();
				
				//Set the ball velocity to rebound off the wall as soon as it has touched it 
	    		if(ball.getYPos() < (wall.getBounds().getMaxY()+ball.getRadius()*2)&& ball.getYPos()> wall.getBounds().getMaxY()){
	    			ball.setYVelocity(-1*ball.getYVelocity());
	    		}
	    		else if(ball.getYPos() > (wall.getBounds().getMinY()-ball.getRadius()*2)&& ball.getYPos()< wall.getBounds().getMinY()){
	    			ball.setYVelocity(-1*ball.getYVelocity());
	    		}
	    		else if(ball.getXPos() < (wall.getBounds().getMaxX()+ball.getRadius()*2)&& ball.getXPos()> wall.getBounds().getMaxX()){
	    			ball.setXVelocity(-1*ball.getXVelocity());
	    		}
	    		else if(ball.getXPos() > (wall.getBounds().getMinX()-ball.getRadius()*2)&& ball.getXPos()< wall.getBounds().getMinX()){
	    			ball.setXVelocity(-1*ball.getXVelocity());
	    		}
			}
    	}
	}
	
	
	void checkWarlordCollision(Warlord warlord){
		if(ball.getNode().intersects(warlord.getBounds())){//Ball touches warlord somewhere
			numberWarlords--; //Warlord has effectively been killed when they are hit by the ball
			warlord.killWarlord();
			
			//Set the ball velocity to rebound off the warlord as soon as it has touched it
    		if(ball.getYPos() < (warlord.getBounds().getMaxY()+ball.getRadius()*2)&& ball.getYPos()> warlord.getBounds().getMaxY()){
    			ball.setYVelocity(-1*ball.getYVelocity());
    		}
    		else if(ball.getYPos() > (warlord.getBounds().getMinY()-ball.getRadius()*2)&& ball.getYPos()< warlord.getBounds().getMinY()){
    			ball.setYVelocity(-1*ball.getYVelocity());
    		}
    		
    		else if(ball.getXPos() < (warlord.getBounds().getMaxX()+ball.getRadius()*2)&& ball.getXPos()> warlord.getBounds().getMaxX()){
    			ball.setXVelocity(-1*ball.getXVelocity());
    		}
    		
    		else if(ball.getXPos() > (warlord.getBounds().getMinX()-ball.getRadius()*2)&& ball.getXPos()< warlord.getBounds().getMinX()){
    			ball.setXVelocity(-1*ball.getXVelocity());
    		}
    	}
	}
	
	boolean checkPaddleCollision(){
		if(ball.getNode().intersects(paddle.getBounds())){ //ball touches paddle
			
			//Set the ball velocity to rebound off the paddle as soon as it touches it
    		if(ball.getYPos() < (paddle.getBounds().getMaxY()+ball.getRadius()*2)&& ball.getYPos()> paddle.getBounds().getMaxY()){
    			ball.setYVelocity(-1*ball.getYVelocity());
    		}
    		
    		else if(ball.getYPos() > (paddle.getBounds().getMinY()-ball.getRadius()*2)&& ball.getYPos()< paddle.getBounds().getMinY()){
    			ball.setYVelocity(-1*ball.getYVelocity());
    		}
    		
    		else if(ball.getXPos() < (paddle.getBounds().getMaxX()+ball.getRadius()*2)&& ball.getXPos()> paddle.getBounds().getMaxX()){
    			ball.setXVelocity(-1*ball.getXVelocity());
    		}
    		
    		else if(ball.getXPos() > (paddle.getBounds().getMinX()-ball.getRadius()*2)&& ball.getXPos()< paddle.getBounds().getMinX()){
    			ball.setXVelocity(-1*ball.getXVelocity());
    		}
    		return true;
    	}
		return false;
	}
	
    public void tick(){ //controls what happens with each tick of the game animation timer
    	move();
    	checkTime();
    }
    
    public void checkTime() {
    	if(time == 0){
    		finished = true;
    	}
    	time--;	
    }

    /***
     * Determine if the game has finished. Results need only be valid before the start and after the end of a game tick.
     *
     * @return true if no more than one warlord remains alive, or if the time remaining is less than or equal to zero. Otherwise, return false.
     */
    public boolean isFinished(){
    	return finished;
    }

    /***
     * Set the time remaining in the game to the given value in seconds.
     *
     * @param seconds
     */
    public void setTimeRemaining(int seconds){
    	time = seconds;
    }
    
    public Paddle getPaddle(){
    	return paddle;
    }
    
    public void destroyWall(Wall wall){
    	wall.destroy();
    }
	
    public Ball getBall(){
    	return ball;
    }
    
    public Wall getWall(){
    	return wall;
    }
    
    public Warlord getWarlord1(){
    	return warlord1;
    }
    
    public Warlord getWarlord2(){
    	return warlord2;
    }
    
    public void warlordsLeft() {
    	if (numberWarlords == 1) {
    		finished = true;
			if(warlord1.isDead() == true){
				warlord2.win();
			}
			else if (warlord2.isDead() == true) {
				warlord1.win();
			}
    	}
    }
    
    void move(){
    	//check game timeout provision 
		if (time == 0) {
			gameTimeout();
		}
		else {
			//Set velocity directions of ball based on collisions that occur
		  	checkWindowBoundaryCollision();
			checkWarlordCollision(warlord1);
			checkWarlordCollision(warlord2);
			checkPaddleCollision();
	    	checkWallCollision();
	    	
	    	//check the number of warlords left and update game status
	    	warlordsLeft();
		}
		//Once the velocities of the ball have been set, update the actual position of the ball in small increments
		//using a for loop, but within the same game tick.
		for (int i = 0; i < Math.abs(ball.getXVelocity()); i++) {		
			ball.setXPos(ball.getXPos() + (ball.getXVelocity() / Math.abs(ball.getXVelocity())));
			ball.setYPos(ball.getYPos() + (ball.getYVelocity() / Math.abs(ball.getYVelocity())));
			if (checkPaddleCollision() == true) {//check for paddle intersections as the ball moves
				ball.setXPos(ball.getXPos() + (ball.getXVelocity() / Math.abs(ball.getXVelocity())));
				ball.setYPos(ball.getYPos() + (ball.getYVelocity() / Math.abs(ball.getYVelocity())));
				break;
			}
		}
		//Display the ball on the GUI in its new position
		ball.redrawBall();
	}  
    
    public void gameTimeout() {		
		finished = true; //update game status and determine the winner of the game
		if (warlord1.getNumWalls() > warlord2.getNumWalls()) {
			warlord1.win();
		}
		else{
			warlord2.win();
		}
    }
	
	void movePaddleRight(){
		if(getPaddle().xPos > SCREEN_WIDTH - 120) { //when the paddle gets very close to leaving the screen
			getPaddle().setXVelocity(0); //Don't allow the paddle to move
		}
		else {
			getPaddle().setXVelocity(10); //set a constant speed for the paddle
		}
		getPaddle().setXPos(getPaddle().getXVelocity() + getPaddle().getXPos()); //update position of paddle

		//MAY USE THIS LATER
//		for (int i = 0; i < getPaddle().getXVelocity(); i++) {		
//			getPaddle().setXPos(getPaddle().getXPos() + 1);
//		}
	}
	
	void movePaddleLeft(){
		if(getPaddle().xPos < 15) { //when the paddle gets very close to leaving the screen
			getPaddle().setXVelocity(0); //Don't allow the paddle to move
		}
		else {
			getPaddle().setXVelocity(-10); //set a constant speed for the paddle
		}
		getPaddle().setXPos(getPaddle().getXVelocity() + getPaddle().getXPos()); //update position of paddle
		
		//MAY USE THIS LATER
//		for (int i = 0; i < (getPaddle().getXVelocity())*-1; i++) {		
//			getPaddle().setXPos(getPaddle().getXPos() - 1);
//		}
	}
}
