class RoomsController < ApplicationController
  helper_method :sort_column, :sort_direction

  def index
    @rooms = Room.all.order(sort_column + " " + sort_direction)
  end

  def new
    @room = Room.new
  end

  def create
    @room = Room.new(room_params)
    if @room.save
      redirect_to rooms_path
    else
      render :new
    end
  end

private

  def sort_column
    Room.column_names.include?(params[:sort]) ? params[:sort] : "clock"
  end

  def sort_direction
    %w[asc desc].include?(params[:direction]) ? params[:direction] : "asc"
  end

  def room_params
    params.require(:room).permit(:clock, :name, :description, :room)
  end
end
