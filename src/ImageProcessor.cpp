#include "ImageProcessor.h"

ImageProcessor::ImageProcessor(QObject *parent)
    : QObject(parent) {}

ImageProcessor::~ImageProcessor() {}

void ImageProcessor::loadImage(const QString &filePath) {
    if (QFile::exists(filePath)) {
        m_image.load(filePath);
        emit imageLoaded();
    } else {
        qWarning() << "File not found:" << filePath;
    }
}

void ImageProcessor::saveCroppedImage(const QRect &rect, const QString &outputPath) {
    if (!m_image.isNull()) {
        QImage cropped = m_image.copy(rect);
        if (!cropped.save(outputPath)) {
            qWarning() << "Failed to save cropped image to" << outputPath;
        }
    } else {
        qWarning() << "No image loaded.";
    }
}

QImage ImageProcessor::currentImage() const {
    return m_image;
}
