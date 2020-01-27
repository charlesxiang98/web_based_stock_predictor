var express = require("express");
var router  = express.Router();
var Course = require("../models/course");
var middleware = require("../middleware");
var Review = require("../models/review");
var Comment = require("../models/comment");

var multer = require('multer');
var storage = multer.diskStorage({
  filename: function(req, file, callback) {
    callback(null, Date.now() + file.originalname);
  }
});
var imageFilter = function (req, file, cb) {
    // accept image files only
    if (!file.originalname.match(/\.(jpg|jpeg|png|gif)$/i)) {
        return cb(new Error('Only picture file allowed to upload!'), false);
    }
    cb(null, true);
};
var upload = multer({ storage: storage, fileFilter: imageFilter})

var cloudinary = require('cloudinary');
cloudinary.config({ 
    cloud_name: 'qyzh', 
    api_key: 721833945316614, 
    api_secret: 'iGhg5JCItVeHF-NFY5chcc6Wevo'
});
    
// INDEX - show all courses
router.get("/", function (req, res) {
    var noMatch = "";
    if(req.query.search){
        const regex = new RegExp(escapeRegex(req.query.search), 'gi');
        Course.find({name: regex}).skip((perPage * pageNumber) - perPage).limit(perPage).exec(function (err, allCourses) {
            Course.count().exec(function (err, count) {
                if (err) {
                    console.log(err);
                } else {
                        if(allCourses.length < 1){
                            var noMatch = "No results found😥Please try again";
                        }
                        res.render("courses/index", {
                            courses: allCourses,
                            noMatch: noMatch,
                            current: pageNumber,
                            pages: Math.ceil(count / perPage),
                            page: 'courses'
                        });
                    }
                }
            );
        });
    }else{
        var perPage = 8;
        var pageQuery = parseInt(req.query.page);
        var pageNumber = pageQuery ? pageQuery : 1;
        Course.find({}).skip((perPage * pageNumber) - perPage).limit(perPage).exec(function (err, allCourses) {
            Course.count().exec(function (err, count) {
                if (err) {
                    console.log(err);
                } else {
                    res.render("courses/index", {
                        courses: allCourses,
                        noMatch: noMatch,
                        current: pageNumber,
                        pages: Math.ceil(count / perPage),
                        page: 'courses'
                    });
                }
            });
        });
    }
});

//CREATE - add new course to DB
router.post("/", middleware.isLoggedIn, upload.single('image'), function(req, res) {
    cloudinary.uploader.upload(req.file.path, function(result) {
        var name = req.body.name;
    var price = req.body.price;
    var image = req.body.image;
    var desc = req.body.description;
    var author = {
        id: req.user._id,
        username: req.user.username
    }
    var newCourse = {name: name, price, image: image, description: desc, author:author}
      // add cloudinary url for the image to the course object under image property
      req.body.course.image = result.secure_url;
      // add author to course
      req.body.course.author = {
        id: req.user._id,
        username: req.user.username
      }
      Course.create(req.body.course, function(err, course) {
        if (err) {
          req.flash('error', err.message);
          return res.redirect('back');
        }
         req.flash("success", "Course added!");
        res.redirect('/courses/' + course.id);
      });
    });
});

//NEW - show form to create new course
router.get("/new", middleware.isLoggedIn, function(req, res){
   res.render("courses/new"); 
});

// SHOW - shows more info about one course
router.get("/:id", function (req, res) {
    //find the course with provided ID
    Course.findById(req.params.id).populate("comments").populate({
        path: "reviews",
        options: {sort: {createdAt: -1}}
    }).exec(function (err, foundCourse) {
        if (err) {
            console.log(err);
        } else {
            //render show template with that course
            res.render("courses/show", {course: foundCourse});
        }
    });
});

// EDIT Course ROUTE
router.get("/:id/edit", middleware.checkCourseOwnership, function(req, res){
    Course.findById(req.params.id, function(err, foundCourse){
        res.render("courses/edit", {course: foundCourse});
    });
});

// UPDATE Course ROUTE
router.put("/:id", middleware.checkCourseOwnership, upload.single("image"), function (req, res) {
        delete req.body.course.rating;
        cloudinary.uploader.upload(req.file.path, function (result) {
            if (req.file.path) {
                // add cloudinary url for the image to the course object under image property
                req.body.course.image = result.secure_url;
            }
            var newData = { name: req.body.course.name, image: req.body.course.image, description: req.body.course.description, price: req.body.course.price};
            //Updated Data Object
            Course.findByIdAndUpdate(req.params.id, { $set: newData }, function (err, course) {
                if (err) {
                    //Flash Message
                    req.flash("error", err.message);
                    //Redirects Back
                    res.redirect("back");
                }
                else {
                    //Flash Message
                    req.flash("success", "Course updated!");
                    //Redirects To Edited Course
                    res.redirect("/courses/" + course._id);
                }
            }); //End Course/findBoyIdAndUpdate
        }); //Ends Cloudinary Image Upload
}); //Ends Put Router

// DESTROY Course ROUTE
router.delete("/:id",middleware.checkCourseOwnership, function(req, res){
   Course.findById(req.params.id, function (err, course) {
        if (err) {
            res.redirect("/courses");
        } else {
            // deletes all comments associated with the course
            Comment.remove({"_id": {$in: course.comments}}, function (err) {
                if (err) {
                    console.log(err);
                    return res.redirect("/courses");
                }
                // deletes all reviews associated with the course
                Review.remove({"_id": {$in: course.reviews}}, function (err) {
                    if (err) {
                        console.log(err);
                        return res.redirect("/courses");
                    }
                    //  delete the course
                    course.remove();
                    req.flash("success", "Course deleted successfully!");
                    res.redirect("/courses");
                });
            });
        }
    });
});

function escapeRegex(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
};

module.exports = router;