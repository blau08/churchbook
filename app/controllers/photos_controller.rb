class PhotosController < ApplicationController
  require 'flickraw'

  before_action :set_photo, only: [:show, :destroy]
  before_action :set_flickr, only: [:create, :destroy]

  def index
    @photos = Photo.all
  end

  def show
  end

  def new
    @photo = Photo.new
  end

  def create
    photo_id = flickr.upload_photo params[:photo].tempfile.path, :title => 'Title', :description => 'Description'
    photo_url = FlickRaw.url_o(flickr.photos.getInfo(photo_id: photo_id))

    @photo = Photo.new(photo_id: photo_id, photo_url: photo_url)

    respond_to do |format|
      if @photo.save
        format.html { redirect_to @photo, notice: 'Photo was successfully created.' }
        format.json { render action: 'show', status: :created, location: @photo }
      else
        format.html { render action: 'new' }
        format.json { render json: @photo.errors, status: :unprocessable_entity }
      end
    end
  end

  def destroy
    flickr.photos.delete(photo_id: @photo.photo_id)
    @photo.destroy
    respond_to do |format|
      format.html { redirect_to photos_url }
      format.json { head :no_content }
    end
  end

  private
  def set_photo
    @photo = Photo.find(params[:id])
  end

  def set_flickr
    FlickRaw.api_key = ENV['API_KEY']
    FlickRaw.shared_secret = ENV['SHARED_SECRET']

    flickr.access_token = ENV['ACCESS_TOKEN']
    flickr.access_secret = ENV['ACCESS_SECRET']
  end
end
